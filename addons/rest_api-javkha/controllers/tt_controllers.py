from odoo.http import request, Response
# -*- coding: utf-8 -*-
import json
from datetime import date, datetime, timedelta
import logging
import math
import base64

from odoo import http, _, exceptions, fields
from odoo.http import request
from .tt_helper import TortecsSerializer, error_response
from .tt_decorator import route
from .tt_routes import *
from uuid import uuid4

_logger = logging.getLogger(__name__)

TORTECS_API_ENDPOINT = "/tt/api"
TORTECS_API_ENDPOINT_V1 = "/v1"


class TortecsOdooAPIController(http.Controller):
    _tortecs_api_suffix = TORTECS_API_ENDPOINT + TORTECS_API_ENDPOINT_V1
    _tortecs_api_auth_endpoint = _tortecs_api_suffix + tt_auth
    _tortecs_api_model_endpoint = _tortecs_api_suffix + tt_model_data
    _tortecs_api_model_record_endpoint = _tortecs_api_suffix + tt_model_record
    _tortecs_api_model_function_endpoint = _tortecs_api_suffix + tt_model_function
    _tortecs_api_object_endpoint = _tortecs_api_suffix + tt_object_function
    @http.route('/tt/api/v1/authentication', type='http', auth='none', csrf=False, cors='*',methods=["POST", "OPTIONS"])
    def tt_authenticate(self, *args, **post):
        print(post,'-------------')
        try:
            login = post["login"]
        except KeyError:
            raise exceptions.AccessDenied(message='`login` is required.')

        try:
            password = post["password"]
        except KeyError:
            raise exceptions.AccessDenied(message='`password` is required.')

        try:
            db = post["db"]
        except KeyError:
            raise exceptions.AccessDenied(message='`db` is required.')

        http.request.session.authenticate(db, login, password)
        res = request.env['ir.http'].session_info()
        token = self._get_api_token(res.get('uid'))
        print(datetime.strftime(token.get('tt_expired_date'), "%Y-%m-%d %H:%M"),'-------=======================---------======-----')
        
        res.update({
            'api_token': token.get('api_token'),
            "expires_in": datetime.timestamp(token.get('tt_expired_date')),
            "refresh_token": token.get('refresh_token'),
            "refresh_expires_in":  datetime.timestamp(token.get('tt_refresh_expired_date')),
        })
        return res

    def _get_api_token(self, uid):
        token_ids = request.env['tortecs.rest.api'].sudo().search([('tt_user_id', '=', uid)])
        tt_priority = token_ids.mapped('tt_priority')
        if len(tt_priority) > 1:
            tt_priority = tt_priority.sort()[0]
            for token_id in token_ids:
                if tt_priority == token_id.tt_priority:
                    return {'api_token': token_id.tt_api_token,'tt_expired_date' : token_ids.tt_expired_date,'tt_refresh_expired_date' : token_ids.tt_refresh_expired_date, 'refresh_token': token_id.tt_refresh_token}
                else:
                    return False
        else:
            return {'api_token': token_ids.tt_api_token, 'tt_expired_date' : token_ids.tt_expired_date,'tt_refresh_expired_date' : token_ids.tt_refresh_expired_date, 'refresh_token': token_ids.tt_refresh_token}

    @route(_tortecs_api_model_function_endpoint, type='json', auth='user', methods=["POST"], csrf=False)
    def tt_call_model_function(self, model, function, **post):
        args = []
        kwargs = {}
        if "args" in post:
            args = post["args"]
        if "kwargs" in post:
            kwargs = post["kwargs"]
        model = request.env[model]
        result = getattr(model, function)(*args, **kwargs)
        return result

    @route(_tortecs_api_object_endpoint, type='json', auth='user', methods=["POST"], csrf=False)
    def tt_call_obj_function(self, model, rec_id, function, **post):
        args = []
        kwargs = {}
        if "args" in post:
            args = post["args"]
        if "kwargs" in post:
            kwargs = post["kwargs"]
        obj = request.env[model].browse(rec_id).ensure_one()
        result = getattr(obj, function)(*args, **kwargs)
        return result

    @route(_tortecs_api_model_endpoint, type='http', auth='none', methods=['GET'], csrf=False)
    def tt_get_model_data(self, model, **params):
        try:
            records = request.env[model].search([])
        except KeyError as e:
            msg = "The model `%s` does not exist." % model
            res = error_response(e, msg)
            return http.Response(
                json.dumps(res),
                status=200,
                mimetype='application/json'
            )
        if "query" in params:
            query = params["query"]
        else:
            query = "{*}"

        if "order" in params:
            orders = json.loads(params["order"])
        else:
            orders = ""

        if "filter" in params:
            filters = json.loads(params["filter"])
            records = request.env[model].search(filters, order=orders)

        prev_page = None
        next_page = None
        total_page_number = 1
        current_page = 1

        if "page_size" in params:
            page_size = int(params["page_size"])
            count = len(records)
            total_page_number = math.ceil(count / page_size)

            if "page" in params:
                current_page = int(params["page"])
            else:
                current_page = 1  # Default page Number
            start = page_size * (current_page - 1)
            stop = current_page * page_size
            records = records[start:stop]
            next_page = current_page + 1 \
                if 0 < current_page + 1 <= total_page_number \
                else None
            prev_page = current_page - 1 \
                if 0 < current_page - 1 <= total_page_number \
                else None

        if "limit" in params:
            limit = int(params["limit"])
            records = records[0:limit]

        try:
            serializer = TortecsSerializer(records, query, many=True)
            data = serializer.data
        except Exception as e:
            print(e,'-')
            res = error_response(e, e.msg)
            return http.Response(
                json.dumps(res),
                status=200,
                mimetype='application/json'
            )

        res = {
            "count": len(records),
            "prev": prev_page,
            "current": current_page,
            "next": next_page,
            "total_pages": total_page_number,
            "result": data
        }
        return http.Response(
            json.dumps(res),
            status=200,
            mimetype='application/json'
        )

    @route(_tortecs_api_model_record_endpoint, type='http', auth='none', methods=['GET'], csrf=False)
    def tt_get_model_record(self, model, rec_id, **params):
        try:
            records = request.env[model].search([])
        except KeyError as e:
            msg = "The model `%s` does not exist." % model
            res = error_response(e, msg)
            return http.Response(
                json.dumps(res),
                status=200,
                mimetype='application/json'
            )

        if "query" in params:
            query = params["query"]
        else:
            query = "{*}"

        record = records.browse(rec_id)

        try:
            serializer = TortecsSerializer(record, query)
            data = serializer.data
        except SyntaxError as e:
            res = error_response(e, e.msg)
            return http.Response(
                json.dumps(res),
                status=200,
                mimetype='application/json'
            )

        return http.Response(
            json.dumps(data),
            status=200,
            mimetype='application/json'
        )

    @route(_tortecs_api_model_endpoint, type='json', auth="user", methods=['POST'], csrf=False)
    def tt_create_model_data(self, model, **post):
        try:
            data = post['data']
        except KeyError:
            msg = "`data` parameter is not found on POST request body"
            raise exceptions.ValidationError(msg)

        try:
            model_to_post = request.env[model]
        except KeyError:
            msg = "The model `%s` does not exist." % model
            raise exceptions.ValidationError(msg)

        # TODO: Handle data validation

        if "context" in post:
            context = post["context"]
            record = model_to_post.with_context(**context).create(data)
        else:
            record = model_to_post.create(data)
        return record.id

    # This is for single record update
    @route(_tortecs_api_model_endpoint, type='json', auth="user", methods=['PUT'], csrf=False)
    def tt_update_model_record(self, model, rec_id, **post):
        try:
            data = post['data']
        except KeyError:
            msg = "`data` parameter is not found on PUT request body"
            raise exceptions.ValidationError(msg)

        try:
            model_to_put = request.env[model]
        except KeyError:
            msg = "The model `%s` does not exist." % model
            raise exceptions.ValidationError(msg)

        if "context" in post:
            try:
                rec = model_to_put.with_context(**post["context"]).browse(rec_id)
            except Exception as ex:
                msg = "There is a singleton error. please ensure the records are unique."
                raise exceptions.ValidationError(msg)
        else:
            rec = model_to_put.browse(rec_id).ensure_one()

        # TODO: Handle data validation
        for field in data:
            if isinstance(data[field], dict):
                operations = []
                for operation in data[field]:
                    if operation == "push":
                        operations.extend(
                            (4, rec_id, _)
                            for rec_id
                            in data[field].get("push")
                        )
                    elif operation == "pop":
                        operations.extend(
                            (3, rec_id, _)
                            for rec_id
                            in data[field].get("pop")
                        )
                    elif operation == "delete":
                        operations.extend(
                            (2, rec_id, _)
                            for rec_id
                            in data[field].get("delete")
                        )
                    else:
                        data[field].pop(operation)  # Invalid operation

                data[field] = operations
            elif isinstance(data[field], list):
                data[field] = [(6, _, data[field])]  # Replace operation
            else:
                pass

        try:
            return rec.write(data)
        except Exception as e:
            # TODO: Return error message(e.msg) on a response
            res = error_response(e, e.msg)
            return http.Response(
                json.dumps(res),
                status=500,
                mimetype='application/json'
            )

    # This is for bulk update
    @route(_tortecs_api_model_record_endpoint, type='json', auth="user", methods=['PUT'], csrf=False)
    def tt_update_multi_model_records(self, model, **post):
        try:
            data = post['data']
        except KeyError:
            msg = "`data` parameter is not found on PUT request body"
            raise exceptions.ValidationError(msg)

        try:
            model_to_put = request.env[model]
        except KeyError:
            msg = "The model `%s` does not exist." % model
            raise exceptions.ValidationError(msg)

        # TODO: Handle errors on filter
        filters = post["filter"]

        if "context" in post:
            recs = model_to_put.with_context(**post["context"]).search(filters)
        else:
            recs = model_to_put.search(filters)

        # TODO: Handle data validation
        for field in data:
            if isinstance(data[field], dict):
                operations = []
                for operation in data[field]:
                    if operation == "push":
                        operations.extend(
                            (4, rec_id, _)
                            for rec_id
                            in data[field].get("push")
                        )
                    elif operation == "pop":
                        operations.extend(
                            (3, rec_id, _)
                            for rec_id
                            in data[field].get("pop")
                        )
                    elif operation == "delete":
                        operations.extend(
                            (2, rec_id, _)
                            for rec_id in
                            data[field].get("delete")
                        )
                    else:
                        pass  # Invalid operation

                data[field] = operations
            elif isinstance(data[field], list):
                data[field] = [(6, _, data[field])]  # Replace operation
            else:
                pass

        if recs.exists():
            try:
                return recs.write(data)
            except Exception as e:
                # TODO: Return error message(e.msg) on a response
                res = error_response(e, e.msg)
                return http.Response(
                    json.dumps(res),
                    status=200,
                    mimetype='application/json'
                )
        else:
            # No records to update
            return True

    # This is for deleting one record
    @route(_tortecs_api_model_endpoint, type='http', auth="user", methods=['DELETE'], csrf=False)
    def tt_delete_model_record(self, model, rec_id, **post):
        try:
            model_to_del_rec = request.env[model]
        except KeyError as e:
            msg = "The model `%s` does not exist." % model
            res = error_response(e, msg)
            return http.Response(
                json.dumps(res),
                status=200,
                mimetype='application/json'
            )

        rec = model_to_del_rec.browse(rec_id)

        try:
            is_deleted = rec.unlink()
            res = {
                "result": is_deleted
            }
            return http.Response(
                json.dumps(res),
                status=200,
                mimetype='application/json'
            )
        except Exception as e:
            res = error_response(e, str(e))
            return http.Response(
                json.dumps(res),
                status=200,
                mimetype='application/json'
            )

    # This is for bulk deletion
    @route(_tortecs_api_model_record_endpoint, type='http', auth="user", methods=['DELETE'], csrf=False)
    def tt_delete_multi_model_records(self, model, **post):
        filters = json.loads(post["filter"])

        try:
            model_to_del_rec = request.env[model]
        except KeyError as e:
            msg = "The model `%s` does not exist." % model
            res = error_response(e, msg)
            return http.Response(
                json.dumps(res),
                status=200,
                mimetype='application/json'
            )

        # TODO: Handle error raised by `filters`
        recs = model_to_del_rec.search(filters)

        try:
            is_deleted = recs.unlink()
            res = {
                "result": is_deleted
            }
            return http.Response(
                json.dumps(res),
                status=200,
                mimetype='application/json'
            )
        except Exception as e:
            res = error_response(e, str(e))
            return http.Response(
                json.dumps(res),
                status=200,
                mimetype='application/json'
            )

    @route(tt_binary_record, type='http', auth="user", methods=['GET'], csrf=False)
    def tt_get_binary_record(self, model, rec_id, field, **post):
        try:
            request.env[model]
        except KeyError as e:
            msg = "The model `%s` does not exist." % model
            res = error_response(e, msg)
            return http.Response(json.dumps(res), status=200, mimetype='application/json')

        rec = request.env[model].browse(rec_id).ensure_one()
        if rec.exists():
            src = getattr(rec, field).decode("utf-8")
        else:
            src = False
        return http.Response(src)

    @http.route('/dangerous/goods', type='http', auth='none', csrf=False, cors='*', methods= ['OPTIONS','GET'])
    def tt_get_dangerous_goods_data(self, **kw):
        data = http.request.env['dangerous.goods'].sudo().search([])
        arr = []
        response = Response()
        for el in data:
            decoded_base64 = base64.b64decode(el.image)
            encoded_base64 = base64.b64encode(decoded_base64)
            base64_image = encoded_base64.decode('utf-8') 
            arr.append({
                'img' : str(base64_image),
                'title' : str(el.title),
                'description' : str(el.description)
            })
        response = Response(json.dumps(arr), content_type='application/json')
        response.headers['Access-Control-Allow-Credentials'] = 'true'
        response.headers['Access-Control-Allow-Origin'] = '*'
        return response

    @http.route('/refresh/token', type='http', auth='none', csrf= False, cors='*')
    def RefreshToken(self, **kw):
        header = request.httprequest.headers
        token = header.get('Authorization')
        data = http.request.env['tortecs.rest.api'].sudo().search([('tt_refresh_token','=',token)])
        data.tt_api_token = uuid4().hex
        obj = {
            'access_token' :  data.tt_api_token,
            'expire_date' : datetime.timestamp(data.tt_expired_date)
        }
        return json.dumps(obj)

    @http.route('/container/information', auth='none', csrf=False, type='http', methods=['GET','OPTIONS'], cors='*')
    def sendData(self, **kw):
        data = http.request.env['container.information'].sudo().search([])
        arr = []
        # "/web/image?model=container.information&id=" + str(el.id) + "&field=container_image"
        for el in data:
            decoded_base64 = base64.b64decode(el.container_image)
            encoded_base64 = base64.b64encode(decoded_base64)
            base64_image = encoded_base64.decode('utf-8')
            arr.append({
                'img' : str(base64_image),
                'title' : str(el.title),
                'height' : str(el.height)
            })
        return json.dumps(arr)

    @http.route('/wagon/types', auth='none', csrf=False, type='http', methods=['GET','OPTIONS'], cors='*')
    def WagonTypes(self, **kw):
        data = http.request.env['wagon.types'].sudo().search([])
        arr = []
        # "/web/image?model=container.information&id=" + str(el.id) + "&field=container_image"
        for el in data:
            decoded_base64 = base64.b64decode(el.image)
            encoded_base64 = base64.b64encode(decoded_base64)
            base64_image = encoded_base64.decode('utf-8')
            arr.append({
                'img' : str(base64_image),
                'title' : str(el.title),
                'height' : str(el.height)
            })
        return json.dumps(arr)

    @http.route('/employees/data', auth='none', csrf=False, type='http', methods=['GET','OPTIONS'], cors='*')
    def EmployeesData(self, **kw):
        data = http.request.env['hr.employee'].sudo().search([])
        arr = []
        # "/web/image?model=container.information&id=" + str(el.id) + "&field=container_image"
        for el in data:
            if el.image_1920:
                decoded_base64 = base64.b64decode(el.image_1920)
                encoded_base64 = base64.b64encode(decoded_base64)
                base64_image = encoded_base64.decode('utf-8')

            arr.append({
                'id': el.id,
                'img' : str(base64_image),
                'phone' : str(el.work_phone),
                'mail' : str(el.work_email),
                'name' : str(el.name),
                'job_title' : str(el.job_title)
            })
        return json.dumps(arr)

    @http.route('/worldwide/news', auth='none', csrf=False, type='http',methods=['GET','OPTIONS'], cors='*')
    def WorldWideNews(self, **kw):
        data = http.request.env['worldwide.news'].sudo().search([])
        arr = []
        # "/web/image?model=container.information&id=" + str(el.id) + "&field=container_image"
        for el in data:
            decoded_base64 = base64.b64decode(el.image)
            encoded_base64 = base64.b64encode(decoded_base64)
            base64_image = encoded_base64.decode('utf-8')
            arr.append({
                'img' : str(base64_image),
                'title' : str(el.title),
                'description' : str(el.description),
                'created_date' : str(el.create_date.strftime('%Y-%m-%d'))
            })
        return json.dumps(arr)

    @route('/trans/types', auth='none', csrf=False, type='http', methods=['GET','OPTIONS'], cors='*')
    def TransTypes(self, **kw):
        print(kw['name'])
        data = http.request.env['mlworldwide.freights'].sudo().search([('customer_id.name', '=', kw['name'])])
        notready = data.sudo().search([('state_id.name', '=', 'Created')])
        ongoing = data.sudo().search([('state_id.name', '=', 'On Going')])
        arrived = data.sudo().search([('state_id.name', '=', 'Arrived')])
        delivered = data.sudo().search([('state_id.name', '=', 'Released')])
        arrived_arr=[]
        for el in arrived:
            helper_tracking_arr=[]
            for track in el.freights_routes_shipment:
                helper_tracking_arr.append({
                    'pointName' : str(track.route_point.name),
                    'ATA' : str(track.ata_date),
                    'ETA' : str(track.eta_date)
                })
            arrived_arr.append({
                'ref' : str(el.ref_num),
                'sender': str(el.shipper_info),
                'terminal': str(el.terminal_id.name),
                'goodsname': str(el.freigths_type[0].type_name),
                'from' : str(el.origin_point_id.name),
                'track' : helper_tracking_arr
            })
        ongoing_arr=[]
        for el in ongoing:
            helper_arr=[]
            for track in el.freights_routes_shipment:
                helper_arr.append({
                    'pointName' : str(track.route_point.name),
                    'ATA' : str(track.ata_date),
                    'ETA' : str(track.eta_date)
                })
            notready_arr.append({
                'ref' : str(el.ref_num),
                'sender': str(el.shipper_info),
                'terminal': str(el.terminal_id.name),
                'goodsname': str(el.freigths_type[0].type_name),
                'from' : str(el.origin_point_id.name),
                'track' : helper_arr
            })
        notready_arr=[]
        for el in notready:
            helper_arr=[]
            for track in el.freights_routes_shipment:
                helper_arr.append({
                    'pointName' : str(track.route_point.name),
                    'ATA' : str(track.ata_date),
                    'ETA' : str(track.eta_date)
                })
            notready_arr.append({
                'ref' : str(el.ref_num),
                'sender': str(el.shipper_info),
                'terminal': str(el.terminal_id.name),
                'goodsname': str(el.freigths_type[0].type_name),
                'from' : str(el.origin_point_id.name),
                'track' : helper_arr
            })
        delivered_arr=[]
        for el in delivered:
            helper_arr=[]
            for track in el.freights_routes_shipment:
                helper_arr.append({
                    'pointName' : str(track.route_point.name),
                    'ATA' : str(track.ata_date),
                    'ETA' : str(track.eta_date)
                })
            notready_arr.append({
                'ref' : str(el.ref_num),
                'sender': str(el.shipper_info),
                'terminal': str(el.terminal_id.name),
                'goodsname': str(el.freigths_type[0].type_name),
                'from' : str(el.origin_point_id.name),
                'track' : helper_arr
            })
        print(notready_arr)
        return json.dumps({
            'arrived' : arrived_arr,
            'ongoing' : ongoing_arr,
            'notready' : notready_arr,
            'delivered' : delivered_arr
        })


    @route('/save/quotation', auth='none', csrf=False, type='http', methods=['POST', 'OPTIONS'] , cors="*")
    def SaveQuotation(self, **kw):
        raw_data = request.httprequest.data
        data = json.loads(raw_data)
        print(data)

        freight_type =  http.request.env['freights.type'].sudo().search([('id','=', str(data.get('type')))])
        taras_types = http.request.env['freights.taras'].sudo().search([('id', '=', str(data.get('taras')))])

        data = http.request.env['saved.inquiry'].sudo().create({
            'customer_id' : 1,
            'origin_term' : data.get('originTerm'),
            'destination_term' : data.get('destTerm'),
            'origin_point_id' : data.get('originPoint'),
            'pickup_address' : data.get('pickUpAddress'),
            'delivery_address' : data.get('deliveryAddress'),
            'destination_point_id' : data.get('destPoint'),
            'shipper_info' : data.get('shipper'),
            'shipper_detail' : data.get('shipperDetails'),
            'hscode_category_id' : data.get('cargoCat'),
            'hs_code' : data.get('hs'),
            'notes' : data.get('goodsName'),
            'freigths_type' : freight_type,
            'gross' : data.get('weight'),
            'temperature' : data.get('temp'),
            'local_remark' : data.get('additionalDetails'),
            'volume': data.get('volume'),
            'package_qty' : data.get('packageQty'),
            'terminal_id' : data.get('terminal'),
            'shipment_qty' : data.get('shipmentQty'),
            'wagon_type_id': data.get('wgnType'),
            'taras_id' : taras_types
        })

        print(data,'-----------------Saved Inquiry')
        return 'Created'

    @route('/form/incoterms', auth='none', csrf=False, type='http',methods=['GET','OPTIONS'], cors='*')
    def FormData(self, **kw):
        print(kw)
        data = http.request.env['account.incoterms'].sudo().search([])
        arr = [' ']
        for el in data:
            arr.append(str(el.code))
        return json.dumps(arr)

    @route('/cargo/category', auth='none', csrf=False, type='http', methods=['GET','OPTIONS'], cors='*')
    def FormDataCargoCategory(self, **kw):
        data = http.request.env['freights.hscode.category'].sudo().search([])
        arr = [' ']
        for el in data:
            arr.append(str(el.name))
        return json.dumps(arr)

    @route('/form/transportation', auth='none', csrf=False, type='http', methods=['GET','OPTIONS'], cors='*')
    def FormDataTransportation(self, **kw):
        data = http.request.env['freights.type'].sudo().search([])
        arr = [' ']
        for el in data:
            arr.append(str(el.type_name))
        return json.dumps(arr)

    @route('/form/route/category', auth='none', csrf=False, type='http',methods=['GET','OPTIONS'], cors='*')
    def FormRouteCategory(self, **kw):
        data = http.request.env['freights.taras'].sudo().search([])
        arr = [' ']
        for el in data:
            arr.append(str(el.name))
        return json.dumps(arr)

    @route('/form/containertypes',website=False, auth='none', csrf=False, type='http',methods=['GET','OPTIONS'], cors='*')
    def FormContainerTypes(self, **kw):
        data = http.request.env['freights.taras'].sudo().search([])
        arr = [' ']
        for el in data:
            arr.append(str(el.name))
        return json.dumps(arr)
    @route('/form/wagon/types',website=False, auth='none', csrf=False, type='http', methods=['GET','OPTIONS'], cors='*')
    def FormWagonTypes(self, **kw):
        data = http.request.env['freights.wagon.type'].sudo().search([])
        arr = [' ']
        for el in data:
            arr.append(str(el.name))
        return json.dumps(arr)

    @route('/saved/inquiry', auth='none', csrf=False, type='json', methods=['GET','OPTIONS'], cors='*')
    def SavedInquiry(self, **kw):
        data = http.request.env['saved.inquiry'].sudo().search([])
        arr = []
        for el in data:
            # name hud zasna!
            arr.append({
                'name' : str(el.hs_code),
                'from': str(el.origin_point_id.name),
                'to': str(el.destination_point_id.name),
                'type': str(el.freigths_type[0].type_name),
                'date': str(el.create_date.strftime('%Y-%m-%d'))
            })
        return json.dumps(arr)

    @route('/quotation', auth='none', csrf=False, type='http', methods=['GET','OPTIONS'], cors='*')
    def Quotation(self, **kw):
        data = http.request.env['mlworldwide.freights'].sudo().search([])
        arr = []
        for el in data:
            helper_arr = []
            for rec in el.freights_quotations:
                if rec.state_id.name == 'Sent' or rec.state_id.name == 'Confirmed' or rec.state_id.name == 'Cancelled':
                    helper_arr.append({
                        'ref': str(rec.quotation_ref_num),
                        'total_rate' : str(rec.total_rate),
                        'type' : str(rec.freights_type_ids.type_name),
                        'childStatus' : str(rec.state_id.name)
                    })
            arr.append({
                    'ref': str(el.ref_num),
                    'type': str(el.freigths_type[0].type_name),
                    'typeIndex' : el.freigths_type[0].id,
                    'date': str(el.create_date.strftime('%Y-%m-%d')),
                    'status': str(el.state_id.name),
                    'from' : str(el.origin_point_id.name),
                    # 'fromIndex' : str(el.origin_point_id.id),
                    'to' : str(el.destination_point_id.name),
                    # 'toIndex' : str(el.destination_point_id.id),
                    'child_quot' : helper_arr
                })
        print(arr)
        return json.dumps(arr)

    @route('/quot/confirm', auth='none', csrf=False, type='json', methods=['POST', 'OPTIONS'], cors='*')
    def QuotConfirm(self, **kw):
        data = http.request.env['mlworldwide.freights'].sudo().search([('ref_num', '=', kw['ref'])])
        for quot in data.freights_quotations:
            if quot.quotation_ref_num == kw['quot_ref']:
                for state in http.request.env['mlworldwide.state'].sudo().search([]):
                    if state.name == 'Confirmed':
                        quot.state_id = state.id
            else:
                for state in http.request.env['mlworldwide.state'].sudo().search([]):
                    if state.name == 'Cancelled':
                        quot.state_id = state.id
        return 'Done'

    @route('/inputvalue/from', auth='none', csrf=False, type='http', methods=['GET','POST', 'OPTIONS'], cors='*')
    def inputvalueFrom(self, **kw):
        data = http.request.env['freights.points'].sudo().search([('name', '=ilike', kw['country']+'%')]) 
        print(kw['country'],'-----')
        arr =[]
        for country in data:
            arr.append({
                'country' : str(country.name),
                'id' : str(country.id)
            })
        return json.dumps(arr)

    @route('/inputvalue/terminal', auth='none', csrf=False, type='http', methods=['GET','OPTIONS'], cors='*')
    def inputvalueTerminal(self, **kw):
        terminals = http.request.env['freights.terminal'].sudo().search([]) 
        arr =[' ']
        for terminal in terminals:
            arr.append(str(terminal.name))
            # arr.append({
            #     'name' : str(terminal.name),
            #     'id' : str(terminal.id)
            # })
        return json.dumps(arr)

    @route('/create/freight', auth='none', csrf=False, type='http', methods=['POST', 'OPTIONS'], cors='*')
    def createFreight(self, **kw):
        raw_data = request.httprequest.data
        data = json.loads(raw_data)
        freight_type =  http.request.env['freights.type'].sudo().search([('id','=', str(data.get('type')))])
        taras_types = http.request.env['freights.taras'].sudo().search([('id', '=', str(data.get('taras')))])
        created_freight = http.request.env['mlworldwide.freights'].sudo().create({
            'customer_id' : 1,
            'origin_term' : data.get('originTerm'),
            'destination_term' : data.get('destTerm'),
            'origin_point_id' : data.get('originPoint'),
            'pickup_address' : data.get('pickUpAddress'),
            'delivery_address' : data.get('deliveryAddress'),
            'destination_point_id' : data.get('destPoint'),
            'shipper_info' : data.get('shipper'),
            'shipper_detail' : data.get('shipperDetails'),
            'hscode_category_id' : data.get('cargoCat'),
            'hs_code' : data.get('hs'),
            'notes' : data.get('goodsName'),
            'freigths_type' : freight_type,
            'gross' : data.get('weight'),
            'temperature' : data.get('temp'),
            'local_remark' : data.get('additionalDetails'),
            'volume': data.get('volume'),
            'package_qty' : data.get('packageQty'),
            'terminal_id' : data.get('terminal'),
            'shipment_qty' : data.get('shipmentQty'),
            'wagon_type_id': data.get('wgnType'),
            'taras_id' : taras_types
        })
        print(created_freight,'+++++++++')
        return 'Created'

    @http.route('/trackFreight', auth='user', csrf=False, type='http', methods=['POST', 'OPTIONS'], cors='*')
    def trackFreight(self, **kw):
        data = http.request.env['freights.route.shipment'].sudo().search([('shipment_id.name','=', kw['id'])], limit=1)
        print(data)
        respond = {
            'id' : str(kw['id']),
            'ATA' : str(data.ata_date),
            'ATD' : str(data.atd_date),
            'point' : data.route_point.name,
            'ETA' : str(data.eta_date),
            'ETD': str(data.etd_date)
        }
        return json.dumps(respond)
    
    @http.route('/feedback', auth='public',website=False, csrf=False, type='http')
    def feedback(self, **kw):
        if kw['agent_id']:
            is_existing = http.request.env['freights.client.feedback'].search(['&',('agent_id','=', int(kw['agent_id'])), ('freight_id','=', int(kw['freight_id']))],limit=1) 
            if is_existing:
                if is_existing.expire_date == False:
                    is_existing.sudo().write({
                        'rate' : kw['rate'],
                        'expire_date' : date.today()
                    })
                d1=datetime.strptime(str(is_existing.expire_date),'%Y-%m-%d') 
                d2=datetime.strptime(str(date.today()),'%Y-%m-%d')
                d3=d2-d1
                date_diff=str(d3.days)
                if int(date_diff) > 7:
                    return 'Sorry Feedback is expired'
                else:
                    is_existing.sudo().write({
                        'rate' : kw['rate']
                    })
                return 'Thanks your feedback`s'
            else:
                return 'Sorry There is not have Feedback'
        else:
            return 'Sorry There is not have Agent'