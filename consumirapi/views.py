from django.shortcuts import render
import requests
import json

# Create your views here.

def api_json(request):
    url = 'http://localhost/api_GTIntegration/api/algranel/getInventario?f_cia=1&f120_referencia=ISOBUTANOL&f150_id=B102&f401_id_ubicacion_aux=BUN-TQ-102&f401_id_lote=21060001'
    r = requests.get(url,headers={
        'Accept': 'application/json',
        })
    
    todos = r.json()
    print(todos)
    return render(request, 'consumirapi/data.html', {'todos': todos})

def api_post(request):
    url = 'http://localhost/api_GTIntegration/api/algranel/ajusteInventario'
    payload =  {"ajuste": 
                        {
                            "f350_id_co": "002",
                            "f350_id_tipo_docto": "AJM",
                            "f350_consec_docto": "1",
                            "f350_fecha": "20211130",
                            "f350_id_tercero": "",
                            "f350_notas": "TEST api",
                            "f450_docto_alterno": "INDO7461",
                            "movimiento": [
                                            {
                                                "f470_id_co": "002",
                                                "f470_id_tipo_docto": "AJM",
                                                "f470_consec_docto": "1",
                                                "f470_nro_registro": "1",
                                                "f470_id_bodega": "B102",
                                                "f470_id_ubicacion_aux": "BUN-TQ-102",
                                                "f470_id_lote": "21060001",
                                                "f470_id_motivo": "",
                                                "f470_id_co_movto": "002",
                                                "f470_id_ccosto_movto": "",
                                                "f470_id_unidad_medida": "KG",
                                                "f470_cant_base": "4000",
                                                "f470_costo_prom_uni": "",
                                                "f470_notas": "TEST API",
                                                "f470_referencia_item": "ISOBUTANOL",
                                                "f470_id_un_movto": "001"
                                            }
                                        ]
                        },
                    "f_cia": "1"
                }
    headers = {'content-type': 'application/json', 'Accept': 'application/json'}
    r = requests.post(url, data=json.dumps(payload), headers=headers)
    mensaje = ""
    if r.status_code == 200:
        mensaje = "Data envida correctamente"
    else:
         mensaje = "Data no envida"

    return render(request, 'consumirapi/data_post.html', {'data':r, 'mensaje':mensaje})
