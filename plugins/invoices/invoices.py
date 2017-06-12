from datetime import datetime

from django.core.exceptions import ObjectDoesNotExist
from django.db import Error
from django.shortcuts import redirect

from conf import app_base
from core.version import Version

env = {}

def init(plugin_env):
	global env
	env = plugin_env
	return (0,0,1)

def urls():
	return [
        ["%s/new_invoice$", "add_info", None], #templatka do wypelnienia informacji o nowej fakturze
        ["%s/add_invoice_file/(?P<id>[a-z]+)/$", "add_file", None], #templatka do wyslania pliku faktury uwaga redirect
        ["%s/show_invoices/", "check_invoices", None], #templatka do wyswietlenia wszystkich faktur i ich przegladania
        ["%s/invoices/", "invoices", None], #templatka do faktur transparency
        ["%s/show_invoice(?P<id>[a-z]+)/$", "show_invoice", None], #templatka do pokazania pojedynczej faktury
        ["%s/download_invoices", "download_all", None] #templatka do pobrania wszystkich faktur
	]

def add_info(rq):
		if rq.method == "GET":
			
	return 0