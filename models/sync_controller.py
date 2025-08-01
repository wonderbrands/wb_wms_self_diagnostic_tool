import json
import requests
import logging
import polar as pl
from io import BytesIO
from datetime import datetime
from odoo import models, fields, api


_logger = logging.getLogger(__name__)
class OMSSyncSaleRules(models.Model):
    _name = "oms.sync.sale.rules"

    last_n_days = fields.Integer(
        string="Last N Days",
        required=True
    )

    each_n_minutes = fields.Integer(
        string="Each N Minutes",
        required=True
    )

    and_previous = fields.Boolean(
        string="And Previous",
    )

class OMSCredentials (models.Model):
    _name = "oms.credentials"

    api_key = fields.Char(
        string="API Key",
        required=True
    )

    api_secret = fields.Char(
        string="API Secret",
        required=True
    )

class OMSSaleController(models.Model):
    _name = "oms.sale.controller"
    
    date = fields.Date(
        string="Date",
        readonly=True
    )

    last_sync_date = fields.Datetime(
        string="Last Sync Date",
        readonly=True
    )

    def call_oms_api(self, credentials, date):
        _logger.info("Call OMS API")
        #Send auth request
        _logger.info("Send auth request")
        try:
            auth_request = requests.post(
                url="https://api-mx.enviopack.com/auth",
                headers={
                    "content-type": "application/x-www-form-urlencoded"
                },
                data={
                    "api-key": credentials.api_key,
                    "secret-key": credentials.api_secret
                }
            )
            response_data = auth_request.json()
            token = response_data.get("token")
            refresh_token = response_data.get("refresh_token")

            if token:
                _logger.info("Token saved successfully")
            else:
                _logger.error("Failed to retrieve token")
                return False

        except Exception as e:
            _logger.error(f"Error calling OMS API: {e}")
            return False

        #Get the excel file
        _logger.info("Get the excel file")
        try:
            excel_request = requests.get(
                url=f"https://api-mx.enviopack.com/pedidos/exportar/init?fecha_desde={date.strftime('%Y-%m-%d')}&fecha_hasta={(date + datetime.timedelta(days=1)).strftime('%Y-%m-%d')}&seccion=distribucion-propia",
                headers={
                    "authorization": f"Bearer {token}"
                }
            )
            response_data = excel_request.json()
            filename = response_data.get("filename")

            if filename:
                _logger.info(f"Excel file {filename} requested successfully")
            else:
                _logger.error("Failed to request Excel file")
                return False
        except:
            _logger.error("Failed to request Excel file")
            return False

        #Check if excel file is ready each 3 seconds
        try:
            while True:
                _logger.info("Check if excel file is ready")
                excel_status_request = requests.get(
                    url=f"https://api-mx.enviopack.com/pedidos/exportar/status?filename={filename}",
                    headers={
                        "authorization": f"Bearer {token}"
                    }
                )
                response_data = excel_status_request.json()
                if response_data.get("estado") == "FIN":
                    _logger.info(f"Excel file {filename} is ready")
                    break
                else:
                    _logger.info(f"Excel file {filename} is not ready, waiting 3 seconds")
                    time.sleep(3)
        except:
            _logger.error("Failed to check if Excel file is ready")
            return False

     
        #Download the excel file
        _logger.info("Download the excel file")
        try:
            download_request = requests.get(
                url=f"https://api-mx.enviopack.com/pedidos/exportar/descargar?access_token={token}&filename={filename}",
                headers={
                    "authorization": f"Bearer {token}"
                },
                stream=True
            )
            response_data = download_request.content
            if response_data:
                _logger.info(f"Excel file {filename} downloaded successfully")
            else:
                _logger.error("Failed to download Excel file")
                return False

            #Save the excel file into a variable
            excel_file = BytesIO(response_data)
            _logger.info(f"Excel file {filename} saved into variable")

            #Process the excel file with polars
            try:
                df = pl.read_excel(excel_file)
                _logger.info(f"Excel file {filename} processed successfully with polars")
                pedidos = df["Pedido"].unique()
                for pedido in pedidos:
                    sale = self.env["sale.order"].search([("name", "=", str(pedido))], limit=1)
                    if sale:
                        sale.write({
                            "status_oms": f"{df.loc[df['pedido'] == pedido, 'Estado'].values[0]}/{df.loc[df['pedido'] == pedido, 'Sub Estado'].values[0]}",
                            "packages": df.loc[df['pedido'] == pedido, 'Productos en el envío'].values[0],
                            "last_oms_sync": datetime.now(),
                        })
                        _logger.info(f"Synced sale {pedido}")
                    else:
                        _logger.error(f"Sale {pedido} not found")

                   
            except:
                _logger.error("Failed to process Excel file with polars")
                return False

        except:
            _logger.error("Failed to download Excel file")
            return False



    @api.model
    def cron_sync_sales(self):
        _logger.info("Cron sync sales started")
        credentials = self.env['oms.credentials'].search([], limit=1)
        if not credentials:
            _logger.info("No credentials found, can't sync OMS")
            return False
        #Check the controller for the last sync date
        dates = self.env['oms.sale.controller'].search([])
        #For each day since today until march 1st 2025
        for day in range(0, (datetime.date.today() - datetime.date(2025, 3, 1)).days):
            #Search the controller for the last sync date
            last_sync_date = dates.filtered(lambda d: d.date == datetime.date.today() - datetime.timedelta(days=day))
            #If the last sync date is not found, create a new one
            if not last_sync_date:
                last_sync_date = self.env['oms.sale.controller'].create({
                    'date': datetime.date.today() - datetime.timedelta(days=day),
                })
                #
                self.call_oms_api(credentials, day)

            #Get the rule that best fits the last sync date (from 0 t 3, 4 to 7..... get the range that best fits)
            rule = self.env['oms.sync.sale.rules'].search([
                ('last_n_days', '>=', day),
            ], limit=1)

            #If the rule is not found, do the one with and previous set to true
            if not rule:
                rule = self.env['oms.sync.sale.rules'].search([
                    ('and_previous', '=', True),
                ], limit=1)

            if not rule:
                _logger.info("No rule found, can't sync OMS")
                return False
            #Check if the minutes rule is greater than the last sync date distance in minutesfrom now
            if rule.each_n_minutes > ((datetime.datetime.now() - last_sync_date.last_sync_date).total_seconds()/60):
                continue

            #Call the OMS API
            self.call_oms_api()

            #Update the last sync date
            last_sync_date.last_sync_date = datetime.datetime.now()
                