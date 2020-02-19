from flask_restful import Resource, reqparse
import models
from flask import request
import json
import uuid
import random
from datetime import datetime
import traceback
from sqlalchemy import exc
import sys

# use models.date... instead of redefining date methods in here

def returnCurrencySymbol(currencyCode):
    currencyDict = {"USD": "$", "GBP": "£", "RWF": "RF"}
    return currencyDict[currencyCode]


class Currencies(Resource):

    def get(self):
        message = {}
        try:
            date = request.args.get('date')
            isDryRun = request.args.get('isDryRun')
            if isDryRun == "true":
                results = models.CurrencyValuationsModel.retrieve_currency(date)
                message['noOfMatches'] = len(results)
                return message, 201
            elif isDryRun == "false":
                result = models.CurrencyValuationsModel.retrieve_currency(date)
                i = 1
                res = []
                for row in result:
                    dicto = {}
                    dicto['code'] = row.CurrencyCode
                    # brokem until all currencies added
                    # dicto['symbol'] = returnCurrencySymbol(row.CurrencyCode)
                    dicto['allowDecimal'] = True
                    dicto['valueInUSD'] = str(row.ValueInUSD)
                    res.append(dicto)
                message['matches'] = res
                return message, 200
            else:
                return {'message': 'Request malformed'}, 400
        except ValueError:
            traceback.print_exc(file=sys.stdout)
            return {'message': 'Date invalid'}, 202
        except exc.IntegrityError:
            return {'message': "An error has occured pertaining to Integrity issues. Please re-enter the parameters"}, 500


class Companies(Resource):

    def get(self):
        message = {}
        try:
            date = request.args.get('date')
            isDryRun = request.args.get('isDryRun')
            if isDryRun == "true":
                results = models.CompanyModel.retrieve_companies_before(date)
                message['noOfMatches'] = results.count()
                return message, 201
            elif isDryRun == "false":
                # check if the date parameter is passed
                if date is None: 
                    # if not, return all companies
                    result = models.CompanyModel.retrieve_all_companies()
                else: 
                    # if so, return all companies that existed on or before the date
                    result = models.CompanyModel.retrieve_companies_before(date)
                i = 1
                res = []
                for row in result:
                    dicto = {}
                    dicto['id'] = row.CompanyCode
                    dicto['name'] = row.CompanyName
                    dicto['dateEnteredIntoSystem'] = row.DateEnteredInSystem
                    # dicto['dateFounded'] = row.DateFounded
                    # dicto['userIDcreatedBy'] = row.UserIDCreatedBy
                    res.append(dicto)
                message['matches'] = res
                return message, 201
            else:
                return {'message': 'Request malformed'}, 400
        except ValueError:
            traceback.print_exc(file=sys.stdout)
            return {'message': 'date invalid'}, 202
        except exc.ProgrammingError:
            traceback.print_exc(file=sys.stdout)
            return {'message':'error occurred'}, 202

    def post(self):
        try:
            json_data = request.data
            data = json.loads(json_data)
            code = str(uuid.uuid4())
            name = data['name']
            user_ID = 1 # placeholder
            # dateFounded = data['dateFounded']
            date_entered = models.formatDate(datetime.now())
            new_company = models.CompanyModel(code, name, date_entered) # should have more parameters, user_ID and date_entered
            new_company.save_to_db()
            userAction = "User has inserted a new record in the Companies table with the ID: " + code
            new_event = models.EventLogModel(userAction, date_entered, user_ID)
            new_event.save_to_db()
            return {'message': 'Company has been added'}, 201
        except exc.IntegrityError:
            traceback.print_exc(file=sys.stdout)
            return {'message' : 'Integrity Error occurred, please re-try entering the parameters'}, 500
        except exc.InterfaceError:
            traceback.print_exc(file=sys.stdout)
            return {'message' : 'Interface Error occurred, please re-try entering the parameters'}, 500

    def patch(self):
        try:
            company_ID = request.args.get('id')
            json_data = request.data
            data = json.loads(json_data)
            name = data['name']
            date_founded = data['dateFounded']
            user_ID = 1 # placeholder
            models.CompanyModel.update_company(company_ID, name, date_founded)
            userAction = "User has updated a record in the Companies table with the ID: " + company_ID
            date_now = models.formatDate(datetime.now())
            new_event = models.EventLogModel(userAction, date_now, user_ID)
            new_event.save_to_db()
            return "success", 200
        except exc.IntegrityError:
            traceback.print_exc(file=sys.stdout)
            return {'message' : 'Integrity Error occurred, please re-try entering the parameters'}, 500

    def delete(self):
        try:
            company_ID = request.args.get('id')
            models.CompanyModel.delete_company(company_ID)
            user_ID = 1 # placeholder
            userAction = "User has deleted a record in the Companies table with the ID: " + company_ID
            date_now = models.formatDate(datetime.now())
            new_event = models.EventLogModel(userAction, date_now, user_ID)
            new_event.save_to_db()
            return "success", 200
        except exc.IntegrityError:
            traceback.print_exc(file=sys.stdout)
            return {'message' : 'Integrity Error occurred, please re-try entering the parameters'}, 500


class Products(Resource):

    def get(self):
        message = {}
        try:
            date =  request.args.get('date')
            isDryRun = request.args.get('isDryRun')
            if isDryRun == "true":
                # need error handling to deal with ValueError raised
                result = models.ProductModel.retrieve_products_on_date(date)
                message = {"noOfMatches" : result.count()}
                return message, 201
            elif isDryRun == "false":
                result = models.ProductModel.retrieve_products_on_date(date)
                i = 1
                res = []
                for row in result:
                    dicto = {}
                    dicto['id'] = row.ProductID
                    dicto['name'] = row.ProductName
                    dicto['companyID'] = row.CompanyCode
                    dicto['valueInUSD'] = str(row.ProductPrice)
                    # dicto['dateEnteredIntoSystem'] = row.DateEnteredInSystem
                    # dicto['userIDcreatedBy'] = row.UserIDCreatedBy
                    res.append(dicto)
                message['matches'] = res
                return message, 201
            else:
                return {'message': 'Request malformed'}, 400
        except ValueError:
            traceback.print_exc(file=sys.stdout)
            return {'message': 'date invalid'}, 202
        except exc.ProgrammingError:
            traceback.print_exc(file=sys.stdout)
            return {'message': 'error occurred'}, 202

    def post(self):
        try:
            # get the name, value, and company ID from request
            json_data = request.data
            data = json.loads(json_data)
            name = data['name']
            value = data['valueInUSD']
            companyCode = data['companyID']
            # then create the date now
            date_now = models.formatDate(datetime.now())
            # add to product table, date_now used as dateEnteredIntoSystem
            new_product = models.ProductModel(name, date_now)
            new_productID = new_product.save_to_db()
            # add to the product seller table
            new_product_seller = models.ProductSellersModel(new_productID, companyCode)
            new_product_seller.save_to_db()
            # add to the product valuation table, date_used as DateOfValuation
            new_product_valuation = models.ProductValuationsModel(new_productID, value, date_now)
            new_product_valuation.save_to_db()
            # log the action
            userAction = "User has inserted a new record in the Products table with the ID: " + str(new_productID)
            user_ID = 1 # placeholder
            new_event = models.EventLogModel(userAction, date_now, user_ID)
            new_event.save_to_db()
            return {'message': 'product has been added'}, 201
        except exc.IntegrityError:
            traceback.print_exc(file=sys.stdout)
            return {'message': 'error occured'}, 202
        except exc.InterfaceError:
            traceback.print_exc(file=sys.stdout)
            return {'message': 'error occured'}, 202

    def patch(self):
        try:
            product_ID = request.args.get('id')
            json_data = request.data
            data = json.loads(json_data)
            name = data['name']
            value_in_USD = data['valueInUSD']
            company_ID = data['companyID']
            user_ID = 1 # placeholder
            date_now = models.formatDate(datetime.now())
            models.ProductModel.update_product(product_ID, name)
            models.ProductModel.update_product_sellers(product_ID, company_ID)
            models.ProductModel.update_product_valuations(product_ID, value_in_USD, date_now)
            userAction = "User has updated a record in the Products table with the ID: " + product_ID
            new_event = models.EventLogModel(userAction, date_now, user_ID)
            new_event.save_to_db()
            userAction = "User has updated a record in the ProductSellers table with the ID: " + product_ID
            new_event = models.EventLogModel(userAction, date_now, user_ID)
            new_event.save_to_db()
            userAction = "User has updated a record in the ProductValuations table with the ID: " + product_ID
            new_event = models.EventLogModel(userAction, date_now, user_ID)
            new_event.save_to_db()
            return "success", 200
        except exc.IntegrityError:
            traceback.print_exc(file=sys.stdout)
            return {'message' : 'Integrity Error occurred, please re-try entering the parameters'}, 500

    def delete(self):
        try:
            product_ID = request.args.get('id')
            models.ProductModel.delete_product(product_ID)
            user_ID = 1 # placeholder
            userAction = "User has deleted a record in the Products table with the ID: " + product_ID
            date_now = models.formatDate(datetime.now())
            new_event = models.EventLogModel(userAction, date_now, user_ID)
            new_event.save_to_db()
            return "success", 200
        except exc.IntegrityError:
            traceback.print_exc(file=sys.stdout)
            return {'message' : 'Integrity Error occurred, please re-try entering the parameters'}, 500

class Trades(Resource):

    def get(self):
        try:
            try:
                filter = json.loads(request.args.get('filter'))
            except json.JSONDecodeError:
                return {'message': 'malformed filter'}, 400

            # this needs error checking
            isDryRun = request.args.get('isDryRun')

            results = list() # stores results for each query/filter that is applied by the user

            # TODO add dateModified filter
            # TODO all these loops assumes filter[param] is a list, which may not be true if the input is malformed

            if 'dateCreated' in filter:
                results.append(models.DerivativeTradesModel.get_trades_between(filter['dateCreated'][0], filter['dateCreated'][1]))

            if 'tradeID' in filter:

                    id = filter['tradeID']
                    results.append(models.DerivativeTradesModel.get_trade_with_ID(id))

            if 'buyingParty' in filter:
                for id in filter['buyingParty']:
                    results.append(models.DerivativeTradesModel.get_trades_bought_by(id))

            if 'sellingParty' in filter:
                for id in filter['sellingParty']:
                    results.append(models.DerivativeTradesModel.get_trades_sold_by(id))

            if 'product' in filter:
                for id in filter['product']:
                    results.append(models.DerivativeTradesModel.get_trade_by_product(id))

            if 'notionalCurrency' in filter:
                for id in filter['notionalCurrency']:
                    results.append(models.DerivativeTradesModel.get_trades_by_notional_currency(id))

            if 'underlyingCurrency' in filter:
                for id in filter['underlyingCurrency']:
                    results.append(models.DerivativeTradesModel.get_trade_by_underlying_currency(id))

            if 'userIDcreatedBy' in filter:
                for id in filter['userIDcreatedBy']:
                    results.append(models.DerivativeTradesModel.get_trades_by_user(id))

            #performs intersections on each result set from each query to find the filtered results
            final_results = None
            for each in results:
                if final_results is None:
                    final_results = each
                else:
                    final_results = final_results.intersect(each)

            message = {}

            if isDryRun == "true":
                message = {"noOfMatches" : final_results.count()}
                return message, 201
            elif isDryRun == "false":
                i = 1
                res = []
                for row in final_results:
                    dicto = {}
                    dicto['tradeID'] = row.TradeID
                    dicto['product'] = row.Product
                    dicto['quantity'] = row.Quantity
                    dicto['buyingParty'] = row.BuyingParty
                    dicto['sellingParty'] = row.SellingParty
                    dicto['notionalValue'] = row.NotionalValue
                    dicto['notionalCurrency'] = row.NotionalCurrency
                    dicto['underlyingValue'] = row.UnderlyingValue
                    dicto['underlyingCurrency'] = row.UnderlyingCurrency
                    dicto['strikePrice'] = row.StrikePrice
                    dicto['maturityDate'] = row.MaturityDate
                    # dicto['tradeDate'] = row.TradeDate
                    dicto['userIDcreatedBy'] = row.UserIDCreatedBy
                    # dicto['lastModifiedDate'] = row.LastModifiedDate
                    res.append(dicto)
                    i += 1

                message['matches'] = res
                return message, 201
            else:
                return {'message': 'Request malformed'}, 400
        except ValueError:
            traceback.print_exc(file=sys.stdout)
            return {'message': 'Date invalid'}, 202
        except exc.ProgrammingError:
            traceback.print_exc(file=sys.stdout)
            return {'message' : 'error occurred'}, 500

    def post(self):
        try:
            json_data = request.data
            data = json.loads(json_data)
            id = str(uuid.uuid4())
            product = data['product']
            quantity = data['quantity']
            buyingParty = data['buyingParty']
            sellingParty = data['sellingParty']
            notionalValue = data['notionalValue']
            notionalCurrency = data['notionalCurrency']
            underlyingValue = data['underlyingValue']
            underlyingCurrency = data['underlyingCurrency']
            strikePrice = data['strikePrice']
            maturityDate = data['maturityDate']
            DateOfTrade = models.dateFormat(datetime.now())
            user_ID = 1 # placeholder
            new_trade = models.DerivativeTradesModel(id, DateOfTrade, product, buyingParty, sellingParty, notionalValue, quantity, notionalCurrency, maturityDate, underlyingValue, underlyingCurrency, strikePrice, user_ID)

            #make a query to check if the product exists
            result = models.ProductSellersModel.getProductID(product, sellingParty)
            if len(result) == 0:
                print("Product does not exist")
                return {'message' : 'product not found'}, 404

            # need to implement checking if the currencies exist

            #If a the product or stock which the trade is linked to is found, then the trade
            new_tradeID = new_trade.save_to_db()
            assetIDs = [value for value, in result] #results returns a result set object - need to format this // formatted into a list to get the product id // there should only be 1 product id
            new_product_trade = models.ProductTradesModel(new_tradeID, assetIDs[0])
            new_product_trade.save_to_db()

            #Logging the user action
            userAction = "User has inserted a new record in the Trades table with the ID: " + str(new_tradeID)
            dateOfEvent = models.dateFormat(datetime.now())
            new_event = models.EventLogModel(userAction, dateOfEvent, user_ID)
            new_event.save_to_db()
            return {'message': 'trade has been added'}, 201
        except exc.IntegrityError:
            traceback.print_exc(file=sys.stdout)
            return {'message' : 'error occurred'}, 500
        except exc.InterfaceError:
            traceback.print_exc(file=sys.stdout)
            return {'message' : 'error occurred'}, 500

    def patch(self):

        try:
            trade_ID = request.args.get('id')
            json_data = request.data
            data = json.loads(json_data)
            product = data['product']
            quantity = data['quantity']
            buyingParty = data['buyingParty']
            sellingParty = data['sellingParty']
            notionalValue = data['notionalValue']
            notionalCurrency = data['notionalCurrency']
            underlyingValue = data['underlyingValue']
            underlyingCurrency = data['underlyingCurrency']
            maturityDate = data['maturityDate']
            strikePrice = data['strikePrice']

            models.DerivativeTradesModel.update_trade(tradeID, product, buyingParty, sellingParty, notionalValue, notionalCurrency, quantity, maturityDate, underlyingValue, underlyingCurrency, strikePrice)

            #Logging the user action
            userAction = "User has updated a record in the Trades table with the ID: " + trade_ID
            dateOfEvent = models.dateFormat(datetime.now())
            user_ID = 1 # placeholder
            new_event = models.EventLogModel(userAction, dateOfEvent, user_ID)
            new_event.save_to_db()

            return "success", 200

        except exc.IntegrityError:
            return {'message': "error occurred"}, 201

    def delete(self):
        try:
            trade_ID = request.args.get('id')
            models.DerivativeTradesModel.delete_product(trade_ID)
            user_ID = 1 # placeholder
            userAction = "User has deleted a record in the Trades table with the ID: " + trade_ID
            date_now = models.formatDate(datetime.now())
            new_event = models.EventLogModel(userAction, date_now, user_ID)
            new_event.save_to_db()
            return "success", 200
        except exc.IntegrityError:
            traceback.print_exc(file=sys.stdout)
            return {'message' : 'Integrity Error occurred, please re-try entering the parameters'}, 500


class Reports(Resource):

    def get(self):
        test_data = {
            "matches" : [{
                    "date": "2020-02-18T00:28:38.365Z",
                    "content": """dateOfTrade,tradeID,product,buyingParty,sellingParty,notionalAmount,notionalCurrency,quantity,maturityDate,underlyingPrice,underlyingCurrency,strikePrice
01/04/2010 00:00,ACCKXNIA50698568,Scope Lens,AWYB85,UACN81,18120.0,USD,800,07/04/2011,22.65,USD,20.89
01/04/2010 00:00,TFVNUIEV14019758,Stocks,IJPI82,BBAX06,3733800.0,USD,70000,10/07/2013,53.34,USD,57.62
01/04/2010 00:38,SFKFEMNI33385795,Stocks,AMRO66,TGZI54,203496.08,KWD,100,31/01/2012,279.47,USD,2173.46
01/04/2010 00:39,NFPPXKJO32502934,Premium Nanotech,EDYH00,DREA89,920080.0,USD,4000,31/10/2011,230.02,USD,197.94
01/04/2010 00:39,WLLMPGMU67753060,Stocks,NQJL85,BDBU00,563545.77,KZT,900,28/07/2012,158.88,USD,632.4
01/04/2010 00:40,VQYITYKX67468667,Black Materia Orbs,EWUY52,VCSF07,492600.0,USD,60000,02/04/2013,8.21,USD,8.72
01/04/2010 00:40,MVWWGUEO36009262,Stocks,TBVE46,QLMY86,13120100.0,USD,70000,14/04/2011,187.43,USD,205.65"""
                },
                {
                    "date": "2020-02-17T00:28:38.365Z",
                    "content": """dateOfTrade,tradeID,product,buyingParty,sellingParty,notionalAmount,notionalCurrency,quantity,maturityDate,underlyingPrice,underlyingCurrency,strikePrice
01/04/2010 00:12,XNTJSSWX82102942,Stocks,KKGY69,SFZS08,14978600.0,USD,70000,19/06/2013,213.98,USD,236.56
01/04/2010 00:12,SRAKJKES56980699,Stocks,BBJG05,KKZA87,74360.0,USD,2000,05/04/2014,37.18,USD,42.13
01/04/2010 00:16,SHUUQNAF89208519,Stocks,KUWI70,IIZF28,47470.0,USD,500,19/09/2011,94.94,USD,82.87
01/04/2010 00:16,OXXDOFBX41047829,Stocks,SUOX82,FAWI50,19980111.75,HRK,700,27/05/2011,260.54,USD,25251.2
01/04/2010 00:16,LWAKBSFC76100584,Stocks,CMZC67,LBKT00,5691.0,USD,700,05/03/2011,8.13,USD,8.58
01/04/2010 00:17,NAFWJEQM83465255,Muscle Bands,GZED20,EDYH00,2813580.0,USD,9000,26/07/2012,312.62,USD,341.29
01/04/2010 00:17,MNPRZYBF65527748,Stocks,HFLM11,YLGZ72,5832000.0,USD,80000,11/11/2011,72.9,USD,64.03"""
                }
            ]
        }

        #return test_data, 200

        try:
            try:
                filter = json.loads(request.args.get('filter'))
            except json.JSONDecodeError:
                return {'message': 'malformed filter'}, 400

            # this needs error checking
            isDryRun = request.args.get('isDryRun')

            # TODO add dateModified filter
            # TODO all these loops assumes filter[param] is a list, which may not be true if the input is malformed

            # either dateCreated will be passed or nothing will be passed
            if 'dateCreated' in filter:
                results = models.DerivativeTradesModel.get_trades_between(filter['dateCreated'][0], filter['dateCreated'][1])
                noOfMatches = results.count()
                tradeDates = results.distinct(models.DerivativeTradesModel.DateOfTrade).group_by(models.DerivativeTradesModel.DateOfTrade)
            else:
                results = models.DerivativeTradesModel.get_trades_all()
                noOfMatches = len(results)
                tradeDates = models.DerivativeTradesModel.get_all_trade_dates()
            
            if isDryRun == 'true':
                return {'noOfMatches' : noOfMatches}
            elif isDryRun == 'false':
                message = {'matches' : []}
                for each in tradeDates:
                    report = {'date': None, 'content': None}
                    date = str(each.DateOfTrade)
                    formattedDate = datetime.strptime(date, '%Y-%m-%d')
                    isoDate = formattedDate.strftime('%Y-%m-%dT%H:%M:%SZ')
                    print(isoDate)
                    content = """Date Of Trade,Trade ID,Product,Buying Party,Selling Party,Notional Value,Notional Currency,Quantity,MaturityDate,Underlying Value,Underlying Currency,Strike Price\n"""
                    for row in results:
                        content += str(row.DateOfTrade) + "," + str(row.TradeID) + "," + str(row.Product) + "," + str(row.BuyingParty) + "," + str(row.SellingParty) + "," + str(row.NotionalValue) + "," + str(row.NotionalCurrency) + "," + str(row.Quantity) + "," + str(row.MaturityDate) + "," + str(row.UnderlyingValue) + "," + str(row.UnderlyingCurrency) + "," + str(row.StrikePrice) + "\n"                
                        #print(content)
                    report['date'] = isoDate
                    report['content'] = content
                    message['matches'].append(report)
                return message, 200
            else:
                return {'message' : 'Request Malformed'}, 400

        except ValueError:
            traceback.print_exc(file=sys.stdout)
            return {'message': 'Date invalid'}, 202
        except exc.ProgrammingError:
            traceback.print_exc(file=sys.stdout)
            return {'message' : 'error occurred'}, 500

class Rules(Resource):
    def get(self):
        return 1
    def post(self):
        return 1
    def patch(self):
        return 1
    def delete(self):
        return 1

# redundant
class CheckTrade(Resource):
    def post(self):
        return 1
