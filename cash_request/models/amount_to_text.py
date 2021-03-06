# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.   
#
##############################################################################

from odoo.tools.translate import _

#-------------------------------------------------------------
# French
#-------------------------------------------------------------


to_19_fr = ( u'zéro',  'un',   'deux',  'trois', 'quatre',   'cinq',   'six',
          'sept', 'huit', 'neuf', 'dix',   'onze', 'douze', 'treize',
          'quatorze', 'quinze', 'seize', 'dix-sept', 'dix-huit', 'dix-neuf' )
tens_fr  = ( 'vingt', 'trente', 'quarante', 'Cinquante', 'Soixante', 'Soixante-dix', 'Quatre-vingts', 'Quatre-vingt Dix')
denom_fr = ( '',
          'Mille',     'Millions',         'Milliards',       'Billions',       'Quadrillions',
          'Quintillion',  'Sextillion',      'Septillion',    'Octillion',      'Nonillion',
          'Décillion',    'Undecillion',     'Duodecillion',  'Tredecillion',   'Quattuordecillion',
          'Sexdecillion', 'Septendecillion', 'Octodecillion', 'Icosillion', 'Vigintillion' )

def _convert_nn_fr(val):
    """ convert a value < 100 to French
    """
    if val < 20:
        return to_19_fr[val]
    for (dcap, dval) in ((k, 20 + (10 * v)) for (v, k) in enumerate(tens_fr)):
        if dval + 10 > val:
            if val % 10:
                return dcap + '-' + to_19_fr[val % 10]
            return dcap

def _convert_nnn_fr(val):
    """ convert a value < 1000 to french
    
        special cased because it is the level that kicks 
        off the < 100 special case.  The rest are more general.  This also allows you to
        get strings in the form of 'forty-five hundred' if called directly.
    """
    word = ''
    (mod, rem) = (val % 100, val // 100)
    if rem > 0:
        word = to_19_fr[rem] + ' Cent'
        if mod > 0:
            word += ' '
    if mod > 0:
        word += _convert_nn_fr(mod)
    return word

def french_number(val):
    if val < 100:
        return _convert_nn_fr(val)
    if val < 1000:
         return _convert_nnn_fr(val)
    for (didx, dval) in ((v - 1, 1000 ** v) for v in range(len(denom_fr))):
        if dval > val:
            mod = 1000 ** didx
            l = val // mod
            r = val - (l * mod)
            ret = _convert_nnn_fr(l) + ' ' + denom_fr[didx]
            if r > 0:
                ret = ret + ', ' + french_number(r)
            return ret

def amount_to_text_fr(number, currency):
    number = '%.2f' % number
    units_name = currency
    list = str(number).split('.')
    start_word = french_number(abs(int(list[0])))
    end_word = french_number(int(list[1]))
    cents_number = int(list[1])
    cents_name = (cents_number > 1) and ' Cents' or ' Cent'
    final_result = start_word +' '+units_name+' '+ end_word +' '+cents_name
    return final_result

#-------------------------------------------------------------
# Dutch
#-------------------------------------------------------------

to_19_nl = ( 'Nul',  'Een',   'Twee',  'Drie', 'Vier',   'Vijf',   'Zes',
          'Zeven', 'Acht', 'Negen', 'Tien',   'Elf', 'Twaalf', 'Dertien',
          'Veertien', 'Vijftien', 'Zestien', 'Zeventien', 'Achttien', 'Negentien' )
tens_nl  = ( 'Twintig', 'Dertig', 'Veertig', 'Vijftig', 'Zestig', 'Zeventig', 'Tachtig', 'Negentig')
denom_nl = ( '',
          'Duizend', 'Miljoen', 'Miljard', 'Triljoen', 'Quadriljoen',
           'Quintillion', 'Sextiljoen', 'Septillion', 'Octillion', 'Nonillion',
           'Decillion', 'Undecillion', 'Duodecillion', 'Tredecillion', 'Quattuordecillion',
           'Sexdecillion', 'Septendecillion', 'Octodecillion', 'Novemdecillion', 'Vigintillion' )

def _convert_nn_nl(val):
    """ convert a value < 100 to Dutch
    """
    if val < 20:
        return to_19_nl[val]
    for (dcap, dval) in ((k, 20 + (10 * v)) for (v, k) in enumerate(tens_nl)):
        if dval + 10 > val:
            if val % 10:
                return dcap + '-' + to_19_nl[val % 10]
            return dcap

def _convert_nnn_nl(val):
    """ convert a value < 1000 to Dutch
    
        special cased because it is the level that kicks 
        off the < 100 special case.  The rest are more general.  This also allows you to
        get strings in the form of 'forty-five hundred' if called directly.
    """
    word = ''
    (mod, rem) = (val % 100, val // 100)
    if rem > 0:
        word = to_19_nl[rem] + ' Honderd'
        if mod > 0:
            word += ' '
    if mod > 0:
        word += _convert_nn_nl(mod)
    return word

def dutch_number(val):
    if val < 100:
        return _convert_nn_nl(val)
    if val < 1000:
         return _convert_nnn_nl(val)
    for (didx, dval) in ((v - 1, 1000 ** v) for v in range(len(denom_nl))):
        if dval > val:
            mod = 1000 ** didx
            l = val // mod
            r = val - (l * mod)
            ret = _convert_nnn_nl(l) + ' ' + denom_nl[didx]
            if r > 0:
                ret = ret + ', ' + dutch_number(r)
            return ret

def amount_to_text_nl(number, currency):
    number = '%.2f' % number
    units_name = currency
    list = str(number).split('.')
    start_word = dutch_number(int(list[0]))
    end_word = dutch_number(int(list[1]))
    cents_number = int(list[1])
    cents_name = (cents_number > 1) and 'cent' or 'cent'
    final_result = start_word +' '+units_name+' '+ end_word +' '+cents_name
    return final_result

#-------------------------------------------------------------
# Generic functions
#-------------------------------------------------------------

_translate_funcs = {'fr' : amount_to_text_fr, 'nl' : amount_to_text_nl}

def add_amount_to_text_function(lang, func):
    _translate_funcs[lang] = func
    
#TODO: we should use the country AND language (ex: septante VS soixante dix)
#TODO: we should use en by default, but the translation func is yet to be implemented
def amount_to_text(nbr, lang='fr', currency='euro'):
    """ Converts an integer to its textual representation, using the language set in the context if any.

        Example::
        
            1654: mille six cent cinquante-quatre.
    """
#    if nbr > 1000000:
##TODO: use logger   
#        print "WARNING: number too large '%d', can't translate it!" % (nbr,)
#        return str(nbr)
    
    if not _translate_funcs.has_key(lang):
#TODO: use logger   
        print ("WARNING: no translation function found for lang: '%s'" % (lang,))
#TODO: (default should be en) same as above
        lang = 'fr'
    return _translate_funcs[lang](abs(nbr), currency)

if __name__=='__main__':
    from sys import argv
    
    lang = 'nl'
    if len(argv) < 2:
        for i in range(1,200):
            print (i, ">>", amount_to_text(i, lang))
        for i in range(200,999999,139):
            print (i, ">>", amount_to_text(i, lang))
    else:
        print (amount_to_text(int(argv[1]), lang))


#-------------------------------------------------------------
# Arabic functions
#-------------------------------------------------------------
to_19 = (u'صفر',u'واحد',u'إثنان',u'ثلاثة',u'أربعة',u'خمسة',u'ستة',u'سبعة',u'ثمانية',u'تسعة',u'عشرة',u'أحدعشر',u'إثناعشر',u'ثلاثةعشر',u'أربعةعشر',u'خمسةعشر',u'ستةعشر',u'سبعةعشر',u'ثمانيةعشر',u'تسعةعشر')
tens  = (u'عشرون',u'ثلاثون',u'أربعون',u'خمسون',u'ستون',u'سبعون',u'ثمانون',u'تسعون')
hundreds=('',u'مائـة',u'مائتـان',u'ثلاثمـائة',u'أربعمـائة',u'خمسمـائة',u'ستمائة',u'سبعمائة',u'ثمانمائة',u'تسعمائة')
denom = ('',u'الف',u'مليون',u'مليار',u'تريليون')


def _convert_nn(val):
    if val < 20:
        return to_19[val]
    for (dcap, dval) in ((k, 20 + (10 * v)) for (v, k) in enumerate(tens)):
        if dval + 10 > val:
            if val % 10:
                return  to_19[val % 10]+u' و ' +dcap 
            return dcap


def _convert_nnn(val):
    word = ''
    (mod, rem) = (val % 100, val // 100)
    if rem > 0:
        word = mod > 0 and hundreds[rem] + u' و ' or  hundreds[rem] #to_19[rem] + u' مائة'

    if mod > 0:
        word = word+' '+_convert_nn(mod)
    return word

def english_number(val):
    if val < 1000:
        return val < 100 and _convert_nn(val) or  _convert_nnn(val)
    
    for (didx, dval) in ((v - 1, 1000 ** v) for v in range(len(denom))):
        if dval > val:
            mod = 1000 ** didx
            l = val // mod
            r = val - (l * mod)
            ret = _convert_nnn(l)  +' '+ denom[didx]
            ret = r > 0 and ret + ' '+u' و ' + english_number(r) or ret
            return ret

def amount_to_text(number, units_name=u'جنيه', cents_name=u'قرش'):
    number = '%.2f' % number
    list = str(number).split('.')
    final_result =  u' فقط ' + (english_number(int(list[0])) or ' ') + ' '+ (units_name or ' ')
    if int(list[1]) >0:
    	final_result +=  u' و ' + (english_number(int(list[1])) or ' ') +'  '+((int(list[1]) != 0) and cents_name or ' ' + u' لا غير ')
    return final_result+ u' لا غير '


#-------------------------------------------------------------
# Generic functions
#-------------------------------------------------------------

_translate_funcs = {'ar' : amount_to_text}
    
#TODO: we should use the country AND language (ex: septante VS soixante dix)
#TODO: we should use en by default, but the translation func is yet to be implemented
def amount_to_text(nbr, lang='ar', units_name=u'جنيه', cents_name=u'قرش'):
    """
    Converts an integer to its textual representation, using the language set in the context if any.
    Example:
        1654: thousands six cent cinquante-quatre.
    """
    from odoo import netsvc
#    if nbr > 10000000:
#        netsvc.Logger().notifyChannel('translate', netsvc.LOG_WARNING, _("Number too large '%d', can not translate it"))
#        return str(nbr)
    
    #if not 'lang' in _translate_funcs.keys():
        #netsvc.Logger().notifyChannel('translate', netsvc.LOG_WARNING, _("no translation function found for lang: '%s'" % (lang,)))
        #TODO: (default should be en) same as above
        #lang = 'ar'
    return _translate_funcs[lang](abs(nbr), units_name, cents_name)

if __name__=='__main__':
    from sys import argv
    
    lang = 'ar'
    if len(argv) < 2:
        for i in range(1,200):
            l = int_to_text(i, lang)
        for i in range(200,999999,139):
            l = int_to_text(i, lang)
    else:
        l = int_to_text(int(argv[1]), lang)


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
