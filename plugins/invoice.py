from datetime import datetime, timedelta

from django.core.exceptions import ObjectDoesNotExist
from django.db import Error
from django.shortcuts import redirect


from conf import app_base
from core.version import Version

env = {}


def init(plugin_env):
	global env
	env = plugin_env
	return Version([0, 0, 3, "alpha"])


def urls():
	return [
		["%s/invoice.add$", "add_invoice", "invoice/add_invoice.template.html"],
		["%s/invoice.upload/(?P<id>\d+)/$", "add_invoice_file", "invoice/add_invoice_file.template.html"],
		["%s/invoice.all$", "show_invoices", "invoice/history_invoice.template.html"],
		# podobna do powyzszej["%s/invoices/$", "invoices", None], #templatka do faktur transparency
		["%s/invoice/(?P<id>\d+)/$", "show_invoice", "invoice/show_invoice.template.html"],
		["%s/account.info/(?P<id>\d+)/$", "account_info", "account/account_info.template.html"]
		# ["%s/download_invoices$", "download_all", "invoice/download_invoices.template.html"] #templatka do pobrania wszystkich faktur
	]


def show_invoice(rq, id):
	Invoice = env["getModel"]("Invoice")
	context = {"invoice": Invoice.objects.get(id=id)}
	context.update(env["csrf"](rq))
	return context


def account_info(rq, id):
	Invoice = env["getModel"]("Invoice")
	User = env["getModel"]("User")
	context = {"invoice": Invoice.objects.get(id=id)}
	context.update(env["csrf"](rq))
	invoice = Invoice.objects.get(pk=id)
	user = invoice.member_id
	context = {"invoice": invoice}
	invoice.cashbacked = True
	invoice.save()
	return context


def add_invoice(rq):
	context = {"msg": rq.GET.get("msg"), "error": rq.GET.get("error")}
	context.update(env["csrf"](rq))

	if rq.method == "POST":
		Session = env["getModel"]("Session")
		Invoice = env["getModel"]("Invoice")

		try:
			s = Session.objects.get(session_hash=env["sessid"](rq))

			invoice = Invoice()
			invoice.invoice_number = rq.POST.get("invoice_number")
			invoice.issue_date = rq.POST.get("issue_date")
			invoice.amount = rq.POST.get("amount")
			invoice.with_cashbacked = rq.POST.get("with_cashbacked")
			invoice.member_id = s.user
			invoice.permalink = ""
			invoice.group = rq.POST.get("group")
			invoice.description = rq.POST.get("description")
			invoice.save()
		except Error as e:
			return {"error": "Cannot add new object: %s" % e}
		return redirect("/%s/invoice.upload/%s/" % (app_base, invoice.id))

	return context


def show_invoices(rq):
	Invoice = env["getModel"]("Invoice")

	if rq.method == "GET":
		try:
			last_two_months = datetime.today() - timedelta(days=61)
			invoices = Invoice.objects.filter(issue_date__gte=last_two_months)
			context = {"invoices": sorted(invoices, key=lambda invoice: invoice.issue_date)}
			context.update(env["csrf"](rq))
		except ObjectDoesNotExist:
			return {"error:": "Object does not exist"}
		return context
	if rq.method == "POST":
		try:
			start_date = rq.POST.get("od")
			end_date = rq.POST.get("do")
			invoices = Invoice.objects.filter(issue_date__range=(start_date, end_date))
		except ObjectDoesNotExist:
			return {"error:": "Object does not exist"}
		context = {"invoices": sorted(invoices, key=lambda invoice: invoice.issue_date)}
		context.update(env["csrf"](rq))
		return context


def add_invoice_file(rq, id):
	context = {"msg": rq.GET.get("msg"), "error": rq.GET.get("error")}
	Invoice = env["getModel"]("Invoice")
	context = {"id": id}
	if rq.method == "GET":
		context.update(env["csrf"](rq))
	if rq.method == "POST":
		try:
			invoice = Invoice.objects.get(id=id)
			invoice.file = rq.FILES.get("file")
			invoice.save()
		except Error as e:
			return {"error": "Cannot add new object: %s" % e}
		return redirect("/%s/invoice.all?msg=Saved" % app_base)

	return context
