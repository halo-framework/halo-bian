#!/usr/bin/env python
import logging
import urllib
import uuid
import datetime
import json
from requests import *
# aws
from botocore.exceptions import ClientError
# common
from halo_flask.flask.utilx import Util, strx
from halo_flask.const import HTTPChoice
from halo_flask.flask.mixinx import AbsBaseMixinX as AbsBaseMixin
from halo_flask.exceptions import HaloException, ApiError, BadRequestError
from halo_flask.logs import log_json
from halo_flask.flask.viewsx import AbsBaseLinkX as AbsBaseLink
from halo_flask.response import HaloResponse
# flask
from flask import Response as HttpResponse

from halo_bian.bian.exceptions import BianException
from ..dbutil import *
from ..apis import *
from ..events import *
from halo_flask.settingsx import settingsx

settings = settingsx()

logger = logging.getLogger(__name__)

# @TODO 1. all proprietery code goes to mixin
# @TODO 2. add settings params to extend
# @TODO 3. add settings param data to .env
# @TODO 4. populate static dir
# @TODO 5. populate templates dir
# @TODO 6. add tests

dbaccess = None


def get_dbaccess(req_context):
	global dbaccess
	if dbaccess is None:
		dbaccess = DbUtil(req_context)
	return dbaccess


def get_event_dbaccess():
	req_context = Util.event_req_context
	dbaccess = DbUtil(req_context)
	return dbaccess


def bad_request_view(request):
	logger.debug('system-error 400')
	return HttpResponse(status=400)


def permission_denied_view(request):
	logger.error('system-error 403')
	return HttpResponse(status=403)


def page_not_found_view(request):
	logger.error('system-error 404')
	return HttpResponse(status=404)


def error_view(request):
	logger.error('system-error 500')
	return HttpResponse(status=500)


from halo_bian.bian.abs_bian_srv import AbsBianMixin

from halo_bian.bian.exceptions import BianApiException
from halo_bian.bian.bian import BianResponse,ServiceOperations
from requests.auth import *


class CurrentAccountCurrentAccountFulfillmentArrangementMixin(AbsBianMixin):
	filter_key_values = {None:{'customer-reference-id': 'customerId'}}
	filter_chars = {None:['=']}

	def validate_collection_filter_values(self, bian_request):
		if bian_request:
			for f in bian_request.collection_filter:
				bf = self.break_filter(bian_request,f)
				if bf[self.filter_key] == 'customer-reference-id':
					val = bf[self.filter_val]
					if re.match("(\d{6}$)",val):
						continue
					raise BadRequestError("collection_filter value is not of valid format:"+val)

	def validate_req(self, bian_request):
		super(CurrentAccountCurrentAccountFulfillmentArrangementMixin, self).validate_req(bian_request)
		self.validate_collection_filter_values(bian_request)

	def set_back_api(self, bian_request):
		logger.debug("in set_back_api ")
		return AccountListApi(Util.get_req_context(bian_request.request))

	def set_api_headers(self, bian_request):
		logger.debug("in set_api_headers ")
		headers = {'accept': 'application/json',
				   # 'TSAuthorization': 'TSToken ' + token
				   'apikey': settings.APIKEY #'4gP4CjJIn0co1At81AqBAFzsY9x5ZnCm'
				   }
		return headers

	def set_api_vars(self, bian_request):
		logger.debug("in set_api_vars ")
		ret = {}
		if bian_request.collection_filter:
			for item in bian_request.collection_filter:
				bf = self.break_filter(bian_request,item)
				the_filter_key_values = self.get_filter_key_values(bian_request)
				if bf != None and bf[self.filter_key] in the_filter_key_values:
					if bf[self.filter_key] == "customer-reference-id" and bf[self.filter_sign] == "=":
						ret[the_filter_key_values[bf[self.filter_key]]] = bf[self.filter_val]
		return ret

	def set_api_auth(self, bian_request):
		logger.debug("in set_api_auth ")
		return HTTPBasicAuth('LDBFE1', '12345678')

	def execute_api(self, bian_request, back_api, back_vars, back_headers, back_auth,back_data):
		logger.debug("in execute_api ")
		if back_api:
			timeout = Util.get_timeout(bian_request.request)
			back_api.set_api_params(back_vars)
			try:
				ret = back_api.get(timeout, headers=back_headers)
				return ret
			except ApiError as e:
				raise BianApiException(e)
		return None

	def extract_json(self, bian_request, back_response):
		logger.debug("in extract_json " + str(back_response.status_code))
		if back_response:
			return json.loads(back_response.content)
		return json.loads("{}")

	def create_resp_payload(self, bian_request, back_json):
		logger.debug("in create_resp_payload " + str(back_json))
		if back_json:
			payload = self.map_from_json(back_json, [])
			return payload
		return back_json

	def map_from_json(self, back_json, payload):
		logger.debug("in map_from_json ")
		arr = back_json["body"]
		for rec in arr:
			payload.append(rec["accountId"])
		return payload


class CurrentAccountCurrentAccountFulfillmentArrangementBehaviorQualifiersMixin(AbsBianMixin):

	def do_retrieve(self, bian_request):
		payload = []
		bq = self.behavior_qualifier
		for i in bq.keys():
			val = bq.get(i)
			payload.append(val)
		# payload = bqs
		return BianResponse(bian_request, payload)


class CurrentAccountCurrentAccountFulfillmentArrangementCrReferenceIdBehaviorQualifierMixin(AbsBianMixin):
	filter_key_values = {None:{'amount': 'amount', 'page_start': 'page_start'}}
	filter_chars = {"deposit":['=', '>', '<'],"statements":['=', '>', '<']}

	def do_retrieve_deposit(self, bian_request):
		return self.do_retrieve_bq(bian_request)

	def validate_collection_filter_values(self, bian_request):
		if bian_request:
			for f in bian_request.collection_filter:
				bf = self.break_filter(bian_request,f)
				if bf[self.filter_key] == 'amount':
					val = bf[self.filter_val]
					if re.match("(\d+\\$$)",val):
						continue
					raise BadRequestError("collection_filter value is not of valid format:"+val)

	def validate_req_deposit(self, bian_request):
		logger.debug("in validate_req_deposit ")
		return self.validate_req(bian_request)
		self.validate_collection_filter_values(bian_request)


	def set_back_api_deposit(self, bian_request):
		logger.debug("in set_back_api_deposit ")
		return TrxDtlApi(Util.get_req_context(bian_request.request))

	def set_api_headers(self, bian_request):
		logger.debug("in set_api_headers ")
		headers = {'accept': 'application/json',
				   # 'TSAuthorization': 'TSToken ' + token
				   'apikey': '4gP4CjJIn0co1At81AqBAFzsY9x5ZnCm'
				   }
		return headers

	def set_api_headers_deposit(self, bian_request):
		return self.set_api_headers(bian_request)

	def set_api_vars_deposit(self, bian_request):
		logger.debug("in set_api_vars_deposit ")
		ret = {}
		account_id = bian_request.cr_reference_id
		if account_id:
			ret['accountId'] = account_id
		if bian_request.collection_filter:
			for item in bian_request.collection_filter:
				bf = self.break_filter(bian_request,item)
				the_filter_key_values = self.get_filter_key_values(bian_request)
				if bf != None and bf[self.filter_key] in the_filter_key_values:
					if bf[self.filter_key] == "amount" and bf[self.filter_sign] == ">":
						ret[the_filter_key_values[bf[self.filter_key]]] = bf[self.filter_val]
		return ret

	def set_api_auth_deposit(self, bian_request):
		logger.debug("in set_api_auth_deposit ")
		return HTTPBasicAuth('LDBFE1', '12345678')

	def execute_api_deposit(self, bian_request, back_api, back_vars, back_headers, back_auth,back_data):
		logger.debug("in execute_api_deposit ")
		if back_api:
			timeout = Util.get_timeout(bian_request.request)
			try:
				back_api.set_api_url('ACCOUNT_ID', back_vars['accountId'])
				back_api.set_api_query("bookingDate=")
				logging.debug("bq:" + str(bian_request.collection_filter))
				filter = self.check_in_filter(bian_request, "page_start")
				if filter:
					sign = filter[self.filter_sign]
					start_page = filter[self.filter_val]
					back_api.set_api_query("page_start=" + start_page)
				# back_api.set_api_params("TransactionId="+urllib.parse.quote(" "))
				ret = back_api.get(timeout, headers=back_headers)
				return ret
			except ApiError as e:
				raise BianException(e)
		return None

	def extract_json_deposit(self, bian_request, back_response):
		logger.debug("in extract_json_deposit " + str(back_response.status_code))
		if back_response:
			return json.loads(back_response.content)
		return json.loads("{}")

	def create_resp_payload_deposit(self, bian_request, back_json):
		logger.debug("in create_resp_payload_deposit " + str(back_json))
		if back_json:
			payload = self.map_from_json_deposit(back_json, [])
			return payload
		return back_json

	def set_resp_headers_deposit(self, bian_request, headers):
		return super().set_resp_headers(bian_request, headers)

	"""
	{ create_resp_payload_deposit {'_links': {'self': {'href': 'http://linx102084t6z:8080/ldb/v2/IL0010001/transactions/601801342'}}, 
	'_embedded': {'item': [{'AccountAmount': '-88', 'AccountCurrency': 'ILS', 'AcquireCode': '', 'AfterTransactionBalance': '162', 'ArrangementSatus': 'CURRENT', 'ArrangementType': 'Short Term Deposit', 'BookingDate': '20180501', 'CardNumber': '', 'CashMachineId': '', 'ChequeAccountNumber': '', 'ChequeAccountType': '', 'ChequeBank': '', 'ChequeBranch': '', 'ChequeCrossBankID': '', 'ChequeNumber': '', 'ChequeProofNumber': '', 'ChequeStartDate': '', 'CounterPartyPhoneNumber': '', 'CreditCardPCI': '', 'DepositName': 'BARTEST', 'DepositNumber': '601801980', 'Description': 'Debit Arrangement Account', 'ExchangeRate': '', 'Iban': '', 'LoanName': '', 'LoanNumber': '', 'Mcc4': '', 'MerchantComertialName': '', 'MerchantLegalName': '', 'MerchantNumber': '', 'MtCounterPartyAccountNumber': '', 'MtCounterPartyName': '', 'MtDescription': '', 'OriginAmount': '', 'OriginCurrency': '', 'PrimaryKey': '1', 'ReferenceNumber': 'AA18099TJFMP', 'SecurityName': '', 'SecurityNumber': '', 'TemenosBusinessId': '601801342', 'TransactionCode': '', 'TransactionDatetime': '20190218141309', 'TransactionId': '186777558351189.010001', 'TransactionStatus': 'final', 'Type': 'SavingDeposit', 'ValueDate': '20180501'}, {'AccountAmount': '250.00', 'AccountCurrency': 'ILS', 'AcquireCode': '', 'AfterTransactionBalance': '250', 'ArrangementSatus': '', 'ArrangementType': '', 'BookingDate': '20180409', 'CardNumber': '', 'CashMachineId': '', 'ChequeAccountNumber': '', 'ChequeAccountType': '', 'ChequeBank': '', 'ChequeBranch': '', 'ChequeCrossBankID': '', 'ChequeNumber': '', 'ChequeProofNumber': '', 'ChequeStartDate': '', 'CounterPartyPhoneNumber': '', 'CreditCardPCI': '', 'DepositName': '', 'DepositNumber': '', 'Description': 'Transfer in', 'ExchangeRate': '', 'Iban': '', 'LoanName': '', 'LoanNumber': '', 'Mcc4': '', 'MerchantComertialName': '', 'MerchantLegalName': '', 'MerchantNumber': '', 'MtCounterPartyAccountNumber': 'PL61015', 'MtCounterPartyName': '', 'MtDescription': '', 'OriginAmount': '250.00', 'OriginCurrency': 'ILS', 'PrimaryKey': '2', 'ReferenceNumber': 'FT18099Y5403', 'SecurityName': '', 'SecurityNumber': '', 'TemenosBusinessId': 'FT18099Y5403', 'TransactionCode': '', 'TransactionDatetime': '20180715164139', 'TransactionId': '184591842860099.000001', 'TransactionStatus': 'final', 'Type': 'PepperSubscriptionBonus', 'ValueDate': '20180409'}]}}", "asctime": "2019-02-24 16:21:12", "filename": "mixin_view.py", "lineno": 213}
{"levelname": "DEBUG", "name": "halo_current_account_service.api.mixin.mixin_view", "message": "in map_from_json {'header': {'data': {'accountId': '84492', 'customerId': '100282', 'accountCurrency': 'USD', 'openingBalance': '82.56'}, 'audit': {'T24_time': 342, 'parse_time': 3}, 'page_start': 1, 'page_token': '201904175868374460.01,99', 'total_size': 1, 'page_size': 99}, 'body': [{'debitCreditIndicator': 'Debit', 'valueDate': 'NOREC1', 'transactionName': 'NOREC', 'transactionTotal': 'HYPHN'}]}", "asctime": "2019-08-13 23:40:57", "filename": "mixin_view.py", "lineno": 257}

	"""

	def map_from_json_deposit(self, back_json, payload):
		logger.debug("in map_from_json " + str(back_json))
		arr = back_json["body"]
		for rec in arr:
			payload.append(rec)
		return payload

	def do_retrieve_statements(self, bian_request):
		return self.do_retrieve_bq(bian_request)

	def validate_req_statements(self, bian_request):
		logger.debug("in validate_req_statements ")
		return self.validate_req(bian_request)

	def set_back_api_statements(self, bian_request):
		logger.debug("in set_back_api_statements ")
		return TrxDtlApi(Util.get_req_context(bian_request.request))

	def set_api_headers(self, bian_request):
		logger.debug("in set_api_headers ")
		headers = {'accept': 'application/json',
				   # 'TSAuthorization': 'TSToken ' + token
				   'apikey': '4gP4CjJIn0co1At81AqBAFzsY9x5ZnCm'
				   }
		return headers

	def set_api_headers_statements(self, bian_request):
		return self.set_api_headers(bian_request)

	def set_api_vars_statements(self, bian_request):
		logger.debug("in set_api_vars_statements ")
		ret = {}
		account_id = bian_request.cr_reference_id
		if account_id:
			ret['accountId'] = account_id
		return ret

	def set_api_auth_statements(self, bian_request):
		logger.debug("in set_api_auth_statements ")
		return HTTPBasicAuth('LDBFE1', '12345678')

	def execute_api_statements(self, bian_request, back_api, back_vars, back_headers, back_auth):
		logger.debug("in execute_api_statements ")
		if back_api:
			timeout = Util.get_timeout(bian_request.request)
			try:
				back_api.set_api_url('ACCOUNT_ID', back_vars['accountId'])
				back_api.set_api_query("bookingDate=")
				logging.debug("bq:" + str(bian_request.collection_filter))
				filter = self.check_in_filter(bian_request, "page_start")
				if filter:
					sign = filter[self.filter_sign]
					start_page = filter[self.filter_val]
					back_api.set_api_query("page_start=" + start_page)
				# back_api.set_api_query("page_start="+bian_request.collection_filter["page_start"])
				# back_api.set_api_params("TransactionId="+urllib.parse.quote(" "))
				ret = back_api.get(timeout, headers=back_headers)
				return ret
			except ApiError as e:
				raise BianException(e)
		return None

	def extract_json_statements(self, bian_request, back_response):
		logger.debug("in extract_json_statements " + str(back_response.status_code))
		if back_response:
			return json.loads(back_response.content)
		return json.loads("{}")

	def create_resp_payload_statements(self, bian_request, back_json):
		logger.debug("in create_resp_payload_statements " + str(back_json))
		if back_json:
			payload = self.map_from_json_statements(back_json, [])
			return payload
		return back_json

	def set_resp_headers_statements(self, bian_request, headers):
		return super().set_resp_headers(bian_request, headers)

	"""
		{"levelname": "DEBUG", "name": "halo_current_account_service.api.mixin.mixin_view", "message": "in map_from_json {'header': {'data': {'accountId': '19666', 'customerId': '100285', 'accountCurrency': 'USD', 'openingBalance': '0'}, 'audit': {'T24_time': 224, 'parse_time': 3}, 'page_start': 1, 'page_token': '201904173945734569.01,99', 'total_size': 1, 'page_size': 99}, 'body': [{'debitCreditIndicator': 'Debit', 'valueDate': 'NOREC1', 'transactionName': 'NOREC', 'transactionTotal': 'HYPHN'}]}", "asctime": "2019-08-19 12:36:08", "filename": "mixin_view.py", "lineno": 359}

		"""

	def map_from_json_statements(self, back_json, payload):
		logger.debug("in map_from_json " + str(back_json))
		arr = back_json["body"]
		for rec in arr:
			payload.append(rec)
		return payload


class CurrentAccountCurrentAccountFulfillmentArrangementCrReferenceIdMixin(AbsBianMixin):
	def validate_req(self, bian_request):
		logger.debug("in validate_req ")
		if bian_request:
			customer_reference_id_and_acct_id = bian_request.cr_reference_id
			if not customer_reference_id_and_acct_id:
				raise BadRequestError("missing value for reference_id")
		return True

	def set_back_api(self, bian_request):
		logger.debug("in set_back_api ")
		return AccountDtlApi(Util.get_req_context(bian_request.request))

	def set_api_headers(self, bian_request):
		logger.debug("in set_api_headers ")
		headers = {'Accept': 'application/json',
				   'TSAuthorization': 'TSToken ' + token}
		return headers

	def set_api_vars(self, bian_request):
		logger.debug("in set_api_vars ")
		ret = {}
		customer_reference_id_and_acct_id = bian_request.cr_reference_id
		customer_id = customer_reference_id_and_acct_id.split("$")[0]
		account_id = customer_reference_id_and_acct_id.split("$")[1]
		if customer_id:
			ret['customer_id'] = customer_id
		if account_id:
			ret['account_id'] = account_id
		return ret

	def set_api_auth(self, bian_request):
		logger.debug("in set_api_auth ")
		return HTTPBasicAuth('LDBFE1', '12345678')

	def execute_api(self, bian_request, back_api, back_vars, back_headers, back_auth):
		logger.debug("in execute_api ")
		if back_api:
			timeout = Util.get_timeout(bian_request.request)
			try:
				back_api.set_api_url('CUSTOMER_ID', back_vars['customer_id'])
				back_api.set_api_url('ACCOUNT_ID', back_vars['account_id'])
				ret = back_api.get(timeout, headers=back_headers, auth=back_auth)
				return ret
			except ApiError as e:
				raise BianException(e)
		return None

	def extract_json(self, back_response):
		logger.debug("in extract_json " + str(back_response.status_code))
		if back_response:
			return json.loads(back_response.content)
		return json.loads("{}")

	def create_resp_payload(self, back_json):
		logger.debug("in create_resp_payload " + str(back_json))
		if back_json:
			payload = self.map_from_json(back_json, {})
			return payload
		return back_json

	# {'_links': {'self': {'href': 'http://linx102084t6z:8080/ldb/v2/IL0010001/customer/201286/account/601801342/summary'}},
	# 'AccountName': 'ASFASFASF',
	# 'AltAcctTypeMvGroup': [{'BranchNumber': '601', 'BankNumber': '10', 'AccountNumber': '000080134213', 'Iban': 'IL280106010000080134213'}],
	# 'Arr': '1000.00!0!1000!0%', 'CreditLimitUsage': '0', 'CurrentAccountCreditLimit': '1000.00', 'Customer': '201286',
	# 'FreeCreditLimit': '1000', 'Id': '601801342', 'LastUpdate': '', 'UsagePercentage': '0%', 'WorkingBalance': '162'}
	"""
	{
  "currentAccountNumber": "BIAN",
  "date": "2018-09-26T05:56:05.007",
  "allowedAccess": "admin",
  "taxReference": "taxid00001",
  "accountType": "current",
  "accountCurrency": "USD",
  "partyReference": "5",
  "bankBranchLocationReference": "for booking purposes",
  "accountStatus": "active",
  "optionType": "Email Statements",
  "productInstanceReference": "1",
  "involvedPartyObligationEntitlement": "partyEntitilement",
  "dateType": "open",
  "accountLimitType": "netting",
  "accountLimit": "50000",
  "involvedPartyReference": "cosigner",
  "customerReference": "CR6789",
  "option": "test@email.com"
}

	"""

	def map_from_json(self, back_json, payload):
		logger.debug("in map_from_json ")
		AltAcctTypeMvGroup = back_json["AltAcctTypeMvGroup"]
		payload["currentAccountNumber"] = AltAcctTypeMvGroup[0]["AccountNumber"]
		payload["date"] = "xxx"
		payload["allowedAccess"] = "xxx"
		payload["taxReference"] = "xxx"
		payload["accountType"] = "current"
		payload["accountCurrency"] = "xxx"
		payload["partyReference"] = back_json["Customer"]
		payload["bankBranchLocationReference"] = AltAcctTypeMvGroup[0]["BranchNumber"]
		payload["accountStatus"] = "active"
		payload["optionType"] = "xxx"
		payload["productInstanceReference"] = "xxx"
		payload["involvedPartyObligationEntitlement"] = "xxx"
		payload["dateType"] = "xxx"
		payload["accountLimitType"] = "xxx"
		payload["accountLimit"] = back_json["FreeCreditLimit"]
		payload["involvedPartyReference"] = "xxx"
		payload["customerReference"] = back_json["Customer"]
		payload["option"] = "xxx"
		return payload


class CurrentAccountCurrentAccountFulfillmentArrangementCrReferenceIdDepositsBqReferenceIdMixin(AbsBianMixin):

	def validate_req(self, bian_request):
		logger.debug("in validate_req ")
		if bian_request:
			acct_id = bian_request.cr_reference_id
			if not acct_id:
				raise BadRequestError("missing value for account_id")
			trx_id = bian_request.bq_reference_id
			if not trx_id:
				raise BadRequestError("missing value for trx_id")
		return True

	def set_back_api(self, bian_request):
		logger.debug("in set_back_api ")
		return TrxDtlApi(Util.get_req_context(bian_request.request))

	def set_api_headers(self, bian_request):
		logger.debug("in set_api_headers ")
		headers = {'Accept': 'application/json',
				   'TSAuthorization': 'TSToken ' + token}
		return headers

	def set_api_vars(self, bian_request):
		logger.debug("in set_api_vars ")
		ret = {}
		account_id = bian_request.cr_reference_id
		if account_id:
			ret['account_id'] = account_id
		trx_id = bian_request.bq_reference_id
		if trx_id:
			ret['trx_id'] = trx_id
			self.trx_id = trx_id
		return ret

	def set_api_auth(self, bian_request):
		logger.debug("in set_api_auth ")
		return HTTPBasicAuth('LDBFE1', '12345678')

	def execute_api(self, bian_request, back_api, back_vars, back_headers, back_auth):
		logger.debug("in execute_api ")
		if back_api:
			timeout = Util.get_timeout(bian_request.request)
			try:
				back_api.set_api_url('ACCOUNT_ID', back_vars['account_id'])
				back_api.set_api_params("upToDate=20190222")
				back_api.set_api_params("TransactionId=" + urllib.parse.quote("" + back_vars['trx_id']) + "")
				ret = back_api.get(timeout, headers=back_headers, auth=back_auth)
				return ret
			except ApiError as e:
				raise BianException(e)
		return None

	def extract_json(self, back_response):
		logger.debug("in extract_json " + str(back_response.status_code))
		if back_response:
			return json.loads(back_response.content)
		return json.loads("{}")

	def create_resp_payload(self, back_json):
		logger.debug("in create_resp_payload " + str(back_json))
		if back_json:
			payload = self.map_from_json(back_json, {})
			return payload
		return back_json

	def set_resp_headers_deposit(self, headers):
		return super().set_resp_headers(headers)

	"""
	{ create_resp_payload_deposit {'_links': {'self': {'href': 'http://linx102084t6z:8080/ldb/v2/IL0010001/transactions/601801342'}}, 
	'_embedded': {'item': [{'AccountAmount': '-88', 'AccountCurrency': 'ILS', 'AcquireCode': '', 'AfterTransactionBalance': '162', 
	'ArrangementSatus': 'CURRENT', 'ArrangementType': 'Short Term Deposit', 'BookingDate': '20180501', 'CardNumber': '', 'CashMachineId': '', 'ChequeAccountNumber': '', 
	'ChequeAccountType': '', 'ChequeBank': '', 'ChequeBranch': '', 'ChequeCrossBankID': '', 'ChequeNumber': '', 'ChequeProofNumber': '', 'ChequeStartDate': '', 
	'CounterPartyPhoneNumber': '', 'CreditCardPCI': '', 'DepositName': 'BARTEST', 'DepositNumber': '601801980', 'Description': 'Debit Arrangement Account', 'ExchangeRate': '', 
	'Iban': '', 'LoanName': '', 'LoanNumber': '', 'Mcc4': '', 'MerchantComertialName': '', 'MerchantLegalName': '', 'MerchantNumber': '', 'MtCounterPartyAccountNumber': '', 
	'MtCounterPartyName': '', 'MtDescription': '', 'OriginAmount': '', 'OriginCurrency': '', 'PrimaryKey': '1', 'ReferenceNumber': 'AA18099TJFMP', 'SecurityName': '', 
	'SecurityNumber': '', 'TemenosBusinessId': '601801342', 'TransactionCode': '', 'TransactionDatetime': '20190218141309', 'TransactionId': '186777558351189.010001', 
	'TransactionStatus': 'final', 'Type': 'SavingDeposit', 'ValueDate': '20180501'}, {'AccountAmount': '250.00', 'AccountCurrency': 'ILS', 'AcquireCode': '', 
	'AfterTransactionBalance': '250', 'ArrangementSatus': '', 'ArrangementType': '', 'BookingDate': '20180409', 'CardNumber': '', 'CashMachineId': '', 
	'ChequeAccountNumber': '', 'ChequeAccountType': '', 'ChequeBank': '', 'ChequeBranch': '', 'ChequeCrossBankID': '', 'ChequeNumber': '', 'ChequeProofNumber': '', 
	'ChequeStartDate': '', 'CounterPartyPhoneNumber': '', 'CreditCardPCI': '', 'DepositName': '', 'DepositNumber': '', 'Description': 'Transfer in', 'ExchangeRate': '', 
	'Iban': '', 'LoanName': '', 'LoanNumber': '', 'Mcc4': '', 'MerchantComertialName': '', 'MerchantLegalName': '', 'MerchantNumber': '', 'MtCounterPartyAccountNumber': 'PL61015', 
	'MtCounterPartyName': '', 'MtDescription': '', 'OriginAmount': '250.00', 'OriginCurrency': 'ILS', 'PrimaryKey': '2', 'ReferenceNumber': 'FT18099Y5403', 'SecurityName': '', 
	'SecurityNumber': '', 'TemenosBusinessId': 'FT18099Y5403', 'TransactionCode': '', 'TransactionDatetime': '20180715164139', 'TransactionId': '184591842860099.000001', 'TransactionStatus': 'final', 'Type': 'PepperSubscriptionBonus', 'ValueDate': '20180409'}]}}", "asctime": "2019-02-24 16:21:12", "filename": "mixin_view.py", "lineno": 213}

{
  "productInstanceReference": "payee account number",
  "amount": {
	"amount": "100",
	"currency": "USD"
  },
  "accountLimitType": "transaction credit",
  "accountLimit": {
	"amount": "100",
	"currency": "USD"
  },
  "payeeReference": "customer",
  "customerReference": "account holder",
  "payeeBankReference": "5",
  "payeeProductInstaceReference": "customer account reference",
  "currency": "USD",
  "valueDate": "2018-09-26T05:56:05.007",
  "depositTransactionReference": "1"
}

	"""

	def map_from_json(self, back_json, payload):
		logger.debug("in map_from_json ")
		arr = back_json["_embedded"]["item"]
		for rec in arr:
			if rec["TransactionId"] == self.trx_id:
				payload = {
					"productInstanceReference": "payee account number",
					"amount": {
						"amount": rec["AccountAmount"],
						"currency": rec["AccountCurrency"]
					},
					"accountLimitType": "transaction credit",
					"accountLimit": {
						"amount": "100",
						"currency": "USD"
					},
					"payeeReference": "customer",
					"customerReference": "account holder",
					"payeeBankReference": "5",
					"payeeProductInstaceReference": "customer account reference",
					"currency": "USD",
					"valueDate": "2018-09-26T05:56:05.007",
					"depositTransactionReference": "1"
				}

		return payload


class CurrentAccountCurrentAccountFulfillmentArrangementCrReferenceIdPaymentsBqReferenceIdMixin(AbsBianMixin):
	pass


class CurrentAccountCurrentAccountFulfillmentArrangementCrReferenceIdStandingOrdersBqReferenceIdMixin(AbsBianMixin):
	pass


class CurrentAccountCurrentAccountFulfillmentArrangementCrReferenceIdDirectDebitsBqReferenceIdMixin(AbsBianMixin):
	pass


class CurrentAccountCurrentAccountFulfillmentArrangementCrReferenceIdSweepsBqReferenceIdMixin(AbsBianMixin):
	pass


class CurrentAccountCurrentAccountFulfillmentArrangementCrReferenceIdInventoriesBqReferenceIdMixin(AbsBianMixin):
	pass


class CurrentAccountCurrentAccountFulfillmentArrangementCrReferenceIdLiensBqReferenceIdMixin(AbsBianMixin):
	pass


class CurrentAccountCurrentAccountFulfillmentArrangementCrReferenceIdInterestsBqReferenceIdMixin(AbsBianMixin):
	pass


class CurrentAccountCurrentAccountFulfillmentArrangementCrReferenceIdFeesBqReferenceIdMixin(AbsBianMixin):
	pass


class CurrentAccountCurrentAccountFulfillmentArrangementCrReferenceIdStatementsBqReferenceIdMixin(AbsBianMixin):
	pass


class CurrentAccountCurrentAccountFulfillmentArrangementCrReferenceIdReportsBqReferenceIdMixin(AbsBianMixin):
	pass


class CurrentAccountCurrentAccountFulfillmentArrangementInitiationMixin(AbsBianMixin):
	pass


class CurrentAccountCurrentAccountFulfillmentArrangementCrReferenceIdUpdationMixin(AbsBianMixin):
	pass


class CurrentAccountCurrentAccountFulfillmentArrangementCrReferenceIdRecordingMixin(AbsBianMixin):
	pass


class CurrentAccountCurrentAccountFulfillmentArrangementCrReferenceIdDepositsBqReferenceIdExecutionMixin(AbsBianMixin):
	bian_action = ServiceOperations.EXECUTE


class CurrentAccountCurrentAccountFulfillmentArrangementCrReferenceIdDepositsExecutionMixin(AbsBianMixin):
	bian_action = ServiceOperations.EXECUTE

	def validate_req(self, bian_request):
		super(CurrentAccountCurrentAccountFulfillmentArrangementCrReferenceIdDepositsExecutionMixin, self).validate_req(bian_request)
		#self.validate_body(bian_request)

	def set_back_api(self, bian_request):
		logger.debug("in set_back_api ")
		return AccountListApi(Util.get_req_context(bian_request.request))

	def set_api_headers(self, bian_request):
		logger.debug("in set_api_headers ")
		headers = {'accept': 'application/json',
				   # 'TSAuthorization': 'TSToken ' + token
				   'apikey': settings.APIKEY #'4gP4CjJIn0co1At81AqBAFzsY9x5ZnCm'
				   }
		return headers

	def set_api_vars(self, bian_request):
		logger.debug("in set_api_vars ")
		ret = {}
		if bian_request.collection_filter:
			for item in bian_request.collection_filter:
				bf = self.break_filter(bian_request,item)
				the_filter_key_values = self.get_filter_key_values(bian_request)
				if bf != None and bf[self.filter_key] in the_filter_key_values:
					if bf[self.filter_key] == "customer-reference-id" and bf[self.filter_sign] == "=":
						ret[the_filter_key_values[bf[self.filter_key]]] = bf[self.filter_val]
		return ret

	def set_api_auth(self, bian_request):
		logger.debug("in set_api_auth ")
		return HTTPBasicAuth('LDBFE1', '12345678')

	#def set_api_data(self, bian_request):
	#	return bian_request.request.data

	def execute_api(self, bian_request, back_api, back_vars, back_headers, back_auth,back_data):
		logger.debug("in execute_api ")
		if back_api:
			timeout = Util.get_timeout(bian_request.request)
			back_api.set_api_params(back_vars)
			try:
				ret = back_api.post(back_data,timeout, headers=back_headers)
				return ret
			except ApiError as e:
				raise BianApiException(e)
		return None

	def extract_json(self, bian_request, back_response):
		logger.debug("in extract_json " + str(back_response.status_code))
		if back_response:
			return json.loads(back_response.content)
		return json.loads("{}")

	def create_resp_payload(self, bian_request, back_json):
		logger.debug("in create_resp_payload " + str(back_json))
		if back_json:
			payload = self.map_from_json(back_json, [])
			return payload
		return back_json

	def map_from_json(self, back_json, payload):
		logger.debug("in map_from_json ")
		arr = back_json["body"]
		for rec in arr:
			payload.append(rec["accountId"])
		return payload


class CurrentAccountCurrentAccountFulfillmentArrangementCrReferenceIdPaymentsBqReferenceIdExecutionMixin(AbsBianMixin):
	pass


class CurrentAccountCurrentAccountFulfillmentArrangementCrReferenceIdPaymentsExecutionMixin(AbsBianMixin):
	pass


class CurrentAccountCurrentAccountFulfillmentArrangementCrReferenceIdStandingOrdersBqReferenceIdRequisitionMixin(
	AbsBianMixin):
	pass


class CurrentAccountCurrentAccountFulfillmentArrangementCrReferenceIdStandingOrdersRequisitionMixin(AbsBianMixin):
	pass


class CurrentAccountCurrentAccountFulfillmentArrangementCrReferenceIdDirectDebitsBqReferenceIdRequisitionMixin(
	AbsBianMixin):
	pass


class CurrentAccountCurrentAccountFulfillmentArrangementCrReferenceIdDirectDebitsRequisitionMixin(AbsBianMixin):
	pass


class CurrentAccountCurrentAccountFulfillmentArrangementCrReferenceIdSweepsBqReferenceIdRequisitionMixin(AbsBianMixin):
	pass


class CurrentAccountCurrentAccountFulfillmentArrangementCrReferenceIdSweepsRequisitionMixin(AbsBianMixin):
	pass


class CurrentAccountCurrentAccountFulfillmentArrangementCrReferenceIdInventoriesBqReferenceIdRequisitionMixin(
	AbsBianMixin):
	pass


class CurrentAccountCurrentAccountFulfillmentArrangementCrReferenceIdInventoriesRequisitionMixin(AbsBianMixin):
	pass


class CurrentAccountCurrentAccountFulfillmentArrangementCrReferenceIdLiensBqReferenceIdRequisitionMixin(AbsBianMixin):
	pass


class CurrentAccountCurrentAccountFulfillmentArrangementCrReferenceIdLiensRequisitionMixin(AbsBianMixin):
	pass

