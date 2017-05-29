# SyZaCz web - plugin loading and initialization

import os
import glob
from django.conf.urls import url
from django.http import HttpResponse
from django.http.response import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.apps import apps
from django.template.context_processors import csrf

from conf import app_base
from core.utils import *
from core.log import log

plugin_env = {
	"version": lambda: (0, 0, 2),
	"get_object_or_404": get_object_or_404,
	"sessid": sessid,
	"log": log,
	"getModel": lambda name: apps.get_model(app_label="core", model_name=name),
	"csrf": csrf
}

plugin_list = []
for f in glob.glob(os.path.dirname(__file__) + "/*"):
	if os.path.isfile(f) and not os.path.basename(f).startswith('_') and not os.path.basename(f).endswith("pyc"):
		plugin_list.append(os.path.basename(f)[:-3])

print plugin_list

for p in plugin_list:
	try:
		__import__(p, locals(), globals())
		ver = globals()[p].init(plugin_env)
		print "Loaded plugin: %s %d.%d.%d" % ((p,) + ver)
	except Exception as e:
		print "Error loading plugin %s: %s" % (p, str(e))


def makeUrls(base_url):
	urls = []
	for p in plugin_list:
		p_urls = globals()[p].urls()
		urls.extend(
			[
				url(
					r"%s" % (u[0] % base_url),
					lambda *args, **kwargs: buildView(globals()[p], u[0] % app_base, u[1], u[2], *args, **kwargs)
				)
				for u in p_urls
			]
		)
	return urls


def buildView(plugin, url, callback, template, *args, **kwargs):
	print "building view for %s" % callback
	if validate_sessid(args[0]):
		context = getattr(plugin, callback)(*args, **kwargs)
		print "VIEWBUILDER: type returned: %s" % type(context)
		if type(context) == HttpResponseRedirect:
			return context
		if template:
			return syzacz_render(template, context)
		else:
			return HttpResponse(context)
	else:
		return session_expired("/%s" % url)
