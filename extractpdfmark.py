#!/usr/bin/env python
import sys, os.path, optparse
import PyPDF2

############################################################
# PDF class
############################################################
class PDF(object):
  ppg = PyPDF2.generic

  def isNULL(self, x):
    if isinstance(x, self.ppg.NullObject):
      return 1
    else:
      return 0

  def isIorF(self, x):
    if isinstance(x, (self.ppg.NumberObject, self.ppg.FloatObject, int, float)):
      return 1
    else:
      return 0

  def GetPageMode(self, fn):
    pagemode = fn.getPageMode()
    if pagemode is None:
      pagemode = "/UseNone" # [TODO] extractpdfmark fallback?
    return pagemode

  def GetNamedDest(self, nd):
    # obtain properties from dictionary
    title = nd.title
    pagenum = pagedict[nd.page.getObject().get("/Contents")]
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
    if self.isNULL(zoom):
      zoom = 0
    # format
    view = '%s' % typ
    if self.isIorF(left):
      view = '%s %s' % (view, left)
    if self.isIorF(bottom):
      view = '%s %s' % (view, bottom)
    if self.isIorF(right):
      view = '%s %s' % (view, right)
    if self.isIorF(top):
      view = '%s %s' % (view, top)
    if self.isIorF(zoom):
      view = '%s %s' % (view, zoom)
    return (title, pagenum, view)

############################################################
# Misc Functions for Main Routine
############################################################
def ProcessOptions():
  usage = """Usage: to be written"""

  version = """Version: to be written"""

  parser = optparse.OptionParser(usage=usage, version=version)
  parser.add_option("-o", "--output",
                    action="store", type="string", dest="output",
                    metavar="OUTPUT.ps",
                    help="Output filename [default=stdout]")
  parser.add_option("-s", "--style",
                    action="store", type="string", dest="style",
                    metavar="STYLE",
                    help="Name style (literal, hex, name) [default=%default]")
  parser.add_option("-e", "--escape",
                    action="store_true", dest="escape", default=False,
                    help="Escape all characters")
  parser.set_defaults(style='literal') # [TODO] extractpdfmark default?
  (options, args) = parser.parse_args()
  if len(args) == 0:
    parser.error("try with the option --help!")
  if not options.style in ['literal', 'hex', 'name']:
    parser.error("invalid style name '%s'!" % options.style)
  return (options, args)

############################################################
# Main Routine
############################################################
if __name__ == '__main__':
  # parse options
  (options, args) = ProcessOptions()
  aPDF = PDF()

  # check file
  fname = args[0]
  if os.path.isfile(fname):
    fp = open(fname, "rb")
  else:
    sys.stderr.write('File %s not found\n' % fname)
    sys.exit(1)

  # read file - begin
  pdf = PyPDF2.PdfFileReader(fp)

  # loop through /Pages
  pagedict = {}
  pages = list(pdf.pages)
  for p in pages:
    pagedict[p.get("/Contents")] = pdf.getPageNumber(p)+1

  # get page mode
  pagemode = aPDF.GetPageMode(pdf)

  # get named destination
  dests = pdf.getOutlines()
  destlist = []
  for dest in dests:
    (title, page, view) = aPDF.GetNamedDest(dest)
    destlist.append({'Title': title, 'Page': page, 'View': view})

  # read file - end
  fp.close()

  # print
  print '[ /PageMode %s /DOCVIEW pdfmark' % pagemode
  for i in sorted(destlist, key=lambda x: x['Title']):
    print '[ /Dest (%s) /Page %s /View [%s] /DEST pdfmark' % (i['Title'], i['Page'], i['View'])
