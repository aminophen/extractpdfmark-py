#!/usr/bin/env python
import sys
import PyPDF2
pdf = PyPDF2.PdfFileReader(open(sys.argv[1], "rb"))
ppg = PyPDF2.generic

# sub
def isIorF(x):
  if isinstance(x, (ppg.NumberObject, ppg.FloatObject, int, float)):
    return 1
  else:
    return 0

# loop through /Pages
pagedict = {}
pages = list(pdf.pages)
for p in pages:
  pagedict[p.get("/Contents")] = pdf.getPageNumber(p)+1

# Get page mode
pagemode = pdf.getPageMode()
if pagemode is None:
  pagemode = "/UseNone" # extractpdfmark fallback?
print '[ /PageMode %s /DOCVIEW pdfmark' % pagemode

# Get named destinations
dests = pdf.getOutlines()
for nd in dests:
  # obtain properties from dictionary
  title = nd.title
  page = pagedict[nd.page.getObject().get("/Contents")]
  typ = nd.typ
  # [TODO] these values can sometimes have `None'?
  left = bottom = right = top = zoom = ''
  if typ == "/XYZ" or typ == "/FitV" or typ == "/FitR" or typ == "/FitBV":
    left = nd.left
  if typ == "/FitR":
    bottom = nd.bottom
  if typ == "/FitR":
    right = nd.right
  if typ == "/XYZ" or typ == "/FitH" or typ == "/FitR" or typ == "/FitBH":
    top = nd.top
  if typ == "/XYZ":
    zoom = nd.zoom
  if isinstance(zoom, ppg.NullObject):
    zoom = 0
  # format
  view = '%s' % typ
  if isIorF(left):
    view = '%s %s' % (view, left)
  if isIorF(bottom):
    view = '%s %s' % (view, bottom)
  if isIorF(right):
    view = '%s %s' % (view, right)
  if isIorF(top):
    view = '%s %s' % (view, top)
  if isIorF(zoom):
    view = '%s %s' % (view, zoom)
  print '[ /Dest (%s) /Page %s /View [%s] /DEST pdfmark' % (title, page, view)
