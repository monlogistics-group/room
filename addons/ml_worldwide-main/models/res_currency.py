# -*- coding: utf-8 -*-
# Copyright 2022 Mon Logistics Group <https://www.mlholding.mn>
# Created by Umbaa. 2022-01-27

import math
from odoo import fields, models, _

class ResCurrency(models.Model):
    _inherit = "res.currency"
    _order = 'sequence asc'

    sequence = fields.Integer(help="Used to order the note stages")

    firstLabels = ["", "нэг", "хоёр", "гурав", "дөрөв", "тав", "зургаа", "долоо", "найм", "ес",]
    secondLabels = ["", "арав", "хорь", "гуч", "дөч", "тавь", "жар", "дал", "ная", "ер"]
    thirdLabels = [
        "",
        "зуу",
        "хоёр зуу",
        "гурван зуу",
        "дөрвөн зуу",
        "таван зуу",
        "зургаан зуу",
        "долоон зуу",
        "найман зуу",
        "есөн зуу"
    ]

    firstTailedLabels = [
        "",
        "нэгэн",
        "хоёр",
        "гурван",
        "дөрвөн",
        "таван",
        "зургаан",
        "долоон",
        "найман",
        "есөн"
    ]
    secondTailedLabels = [
        "",
        "арван",
        "хорин",
        "гучин",
        "дөчин",
        "тавин",
        "жаран",
        "далан",
        "наян",
        "ерөн"
    ]
    thirdTailedLabels = [
        "",
        "нэг зуун",
        "хоёр зуун",
        "гурван зуун",
        "дөрвөн зуун",
        "таван зуун",
        "зургаан зуун",
        "долоон зуун",
        "найман зуун",
        "есөн зуун"
    ]
    
    def Amount2Word(self, amount):
        fourth = math.floor(amount / 1000000000)
        thirdStart = amount - fourth * 1000000000
        third = math.floor(thirdStart / 1000000)
        secondStart = thirdStart - third * 1000000
        second = math.floor(secondStart / 1000)
        firstStart = secondStart - second * 1000
        first = math.floor(firstStart)

        zeroStart = firstStart - first
        zero = math.ceil(zeroStart * 100)

        label = ""
        if (fourth > 0):
            label += self.formatHundred(fourth, True)
            label += "тэрбум "
        
        if (third > 0):
            label += self.formatHundred(third, True)
            label += "сая "
        if (second > 0):
            if (second > 1):
                label += self.formatHundred(second, True)
            if (first > 0):
                label += "мянга "
            else:
                label += "мянган "
            
        currencyLabel = {
            "USD": "доллар",
            "MNT": "төгрөг",
            "EUR": "евро",
            "CNY": "юань",
            "RUB": "рубль"
        }
        floatLabel = {
            "USD": "цент",
            "MNT": "мөнгө",
            "EUR": "цент",
            "CNY": "фен",
            "RUB": "копейк"
        }
        currency = "MNT"
        label += self.formatHundred(first, True)
        label += currencyLabel[currency]
        if zero > 0:
            label += " "
            if zero == 1:
                label += self.firstLabels[zero] + " " + floatLabel[currency]
            else:
                label += self.formatHundred(zero, True)
                label += floatLabel[currency]
            
        return label
    
    def formatHundred(self, value, hasTail):
        third = math.floor(value / 100)
        secondStart = value - third * 100
        second = math.floor(secondStart / 10)
        firstStart = secondStart - second * 10
        first = math.floor(firstStart)
        label = ""
        if (third > 0):
            if (second > 0 or first > 0 or hasTail):
                label += self.thirdTailedLabels[third] + " "
            else:
                label += self.thirdLabels[third] + " "
        if (second > 0):
            if (first > 0 or hasTail):
                label += self.secondTailedLabels[second] + " "
            else:
                label += self.secondLabels[second] + " "
        if (first > 0):
            if (hasTail):
                label += self.firstTailedLabels[first] + " "
            else:
                label += self.firstLabels[first] + " "
            
        return label