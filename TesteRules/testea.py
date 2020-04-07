# coding: utf-8

import json
import sqlite3

order = {
    'totalPrice': 0,
    'pgtoType': 1,
    'items': [
        {
            'codigo': 1,
            'quantidade': 10
        },
        {
            'codigo': 4,
            'quantidade': 1
        }
    ]
}

class TesteA:

    fact = {}
    rules = {}

    def __init__(self, fact, rules, conn):
        self.fact = fact
        self.rules = rules
        self.conn = conn

    def __query(self, query, json_str = False ):
        """Realiza simples selects e retorna Json de resposta"""

        c = self.conn.cursor()
        rows = c.execute(query).fetchall()
        if json_str:
            return json.dumps([dict(ix) for ix in rows], ensure_ascii=False)
        retorno = []
        for ix in rows:
            retorno.append(dict(ix))
        return retorno


    def calculateTotalPrice(self, fact):
        """Calcula o preço total do pedido"""
        print('calculateTotalPrice')
        fact['totalDiscount'] = 0.0
        if fact['pgtoType'] == 1:
            fact['totalDiscount'] = round((fact['totalPrice'] * 0.10), 2)
        fact['totalPrice'] = round((fact['totalPrice'] - fact['totalDiscount']), 2)
        return fact

    def calculateItemPrice(self, fact):
        """Calcula o preco de cada item do pedido"""
        print('calculateItemPrice')
        valorTotal = 0.0
        for i in fact.get('items', []):
            query = 'SELECT produto, pf0 as preco FROM produto WHERE id=%s' % i['codigo']
            rows = self.__query(query)
            i['valorUnitario'] = rows[0].get('preco', 0)
            i['valor'] = round((i['valorUnitario'] * i['quantidade']), 2)
            i['nome'] = rows[0].get('produto', '')
            valorTotal += i['valor']

        fact['totalItems'] = round(valorTotal, 2)
        fact['totalPrice'] = fact['totalItems']
        return fact

    def calcular(self):
        """Processa o calculos dos descontos e preço"""
        print('Processando regras de "%s"' % self.rules.get('name'))
        for r in self.rules.get('rules', []):
            _when = r.get('when', '')
            _then = r.get('then', '')
            if _when and hasattr(self, _then):
                operacao = getattr(self, _then , None)
                if callable(operacao):
                    self.fact = operacao(self.fact)

        return self.fact


if __name__ == '__main__':
    try:
        rules = {}
        with open('files/example.json') as arq:
            rules = json.load(arq)
        conn = sqlite3.connect('files/produtos.db')
        conn.row_factory = sqlite3.Row # This enables column access by name: row['column_name']
        t = TesteA(order, rules, conn)
        order = t.calcular()
        print(json.dumps(order, ensure_ascii=False, indent=2))
    except Exception as e:
        print('ERRO %s' % str(e))
    finally:
        conn.close()