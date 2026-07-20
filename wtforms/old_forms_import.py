# -*- coding: utf-8 -*-
import json
from django.db import connection

def dictfetchall(cursor): 
    "Returns all rows from a cursor as a dict" 
    desc = cursor.description 
    return [
            dict(zip([col[0] for col in desc], row)) 
            for row in cursor.fetchall() 
    ]

def save_xml(apps, schema_editor):
    with connection.cursor() as cursor:
        cursor.execute("select p.id, p.title, f.* from wtforms_formpage f join wagtailcore_page p on p.id = f.page_ptr_id")
        data = json.dumps(dictfetchall(cursor))
        with open('/tmp/old_forms.json', 'w') as f:
            f.write(data)
    
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM wtforms_formfield")
        data = json.dumps(dictfetchall(cursor))
        with open('/tmp/old_form_fields.json', 'w') as f:
            f.write(data)

    
    
def load_xml(apps, schema_editor):    
    table_form = 'wtforms_wtform'
    table_field = 'wtforms_wtformfield'
    
    form_insert_sql = "INSERT INTO "+table_form+"(id, body, thank_you_text, name, title, to_address, from_address, subject) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
    form_field_insert_sql = "INSERT INTO "+table_field+"(sort_order, label, field_type, required, choices, default_value, help_text, page_id) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
    form_last_id_sql = "SELECT nextval('%s_id_seq')" % table_form 
    
    forms={}
    
    with open('/tmp/old_forms.json', 'r') as json_data:   
        d = json.load(json_data)
        for obj in d:
            obj["fields"] = []
            forms[obj["id"]] = obj
            
    
    with open('/tmp/old_form_fields.json', 'r') as json_data:   
        d = json.load(json_data)
        for obj in d:
            forms[obj["page_id"]]["fields"].append(obj)
    
            
    
    for form_id, obj in forms.items():
        with connection.cursor() as cursor:
            cursor.execute(form_last_id_sql)
            page_id = cursor.fetchone()[0]
            print(page_id)
            cursor.execute(form_insert_sql, 
                [page_id, obj["body"], obj["thank_you_text"], obj["title"], obj["page_heading"], 
                 obj["to_address"], obj["from_address"], obj["subject"] ])            
            
            for fld in obj["fields"]:
                cursor.execute(form_field_insert_sql, [fld["sort_order"], fld["label"], fld["field_type"], fld["required"], 
                    fld["choices"], fld["default_value"], fld["help_text"], page_id])
                
            
