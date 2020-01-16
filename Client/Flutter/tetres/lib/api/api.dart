import 'package:flutter/widgets.dart';
import 'package:http/http.dart' as http;
import 'package:tetres/global/global.dart';

export 'api_action_widget.dart';
export 'json_helpers/api_infra.dart';
export 'json_helpers/api_route_list.dart';
export 'json_helpers/api_syscfg.dart';

enum ApiActionState {
  pending,
  success,
  fail,
}

class Api {
//  static Future<String> sendGet({@required String endpoint}) async {
//    try {
//      http.Response res = await http.get(Gbl.serverUrl + endpoint);
//      print("BODY: ${res?.body}");
//      return res.body;
//    } catch (e) {
//      print("Exception [sendGet][$e]");
//    }
//    return null;
//  }

  static Future<http.Response> sendGet({@required String endpoint}) async {
    try {
      http.Response res = await http.get(Gbl.serverUrl + endpoint);
      return res;
    } catch (e) {
      print("Exception [sendGet][$e]");
    }
    return null;
  }

  static Future<http.Response> sendPost(
      {@required String endpoint,
      Map<String, dynamic> headers,
      Map<String, dynamic> bodyData}) async {
    try {
      http.Response res = await http.post(Gbl.serverUrl + endpoint,
          body: bodyData, headers: headers);
      return res;
//      print("BODY: ${res?.body}");
    } catch (e) {}
    return null;
  }
}

class ApiEndPoints {
  static const String isServerOn = "/ticas/ison"; //get
  static const String infra = "/ticas/infra";
  static const String userApiInfo = "/tetres/user/info"; //get
  static const String adminApiInfo = "/tetres/adm/info"; //get
  static const String systemConfigGet = "/tetres/adm/syscfg/get"; //get
  static const String systemConfigUpdate = "/tetres/adm/syscfg/update"; //post
  static const String actionLogList = "/tetres/adm/actionlog/list"; //post
  static const String actionLogProceed = "/tetres/adm/actionlog/proceed"; //get
  static const String adminListRoutes = "/tetres/adm/route/list"; //get
  static const String adminAddRoute = "/tetres/adm/route/add"; //post
}
