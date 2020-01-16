import 'dart:io';

import 'package:flutter/material.dart';
import 'package:tetres/api/api.dart';
import 'package:tetres/api/json_helpers/api_infra.dart';

export 'app_theme.dart';

enum LoginState {
  admin,
  basic,
  none,
}

class Gbl {
  static ApiInfra gblApiInfra;

  static const serverUrl = "http://192.168.1.19:5000";

  static const appDrawerBackToLogin = "Back To Login";
  static const appDrawerRoutes = "Routes";
  static const appDrawerServerConfig = "Server Config";
  static const appDrawerClientConfig = "Client Config";


  static final List<GblListTile> appDrawerTilesAdmin = [
    const GblListTile(title: appDrawerRoutes, icon: Icons.drive_eta),
    const GblListTile(title: appDrawerClientConfig, icon: Icons.settings),
    const GblListTile(title: appDrawerServerConfig, icon: Icons.settings),
    const GblListTile(title: appDrawerBackToLogin, icon: Icons.arrow_back),
  ];

  static final List<GblListTile> appDrawerTilesBasic = [
    const GblListTile(title: appDrawerRoutes, icon: Icons.drive_eta),
    const GblListTile(title: appDrawerClientConfig, icon: Icons.settings),
    const GblListTile(title: appDrawerBackToLogin, icon: Icons.arrow_back),
  ];

  static List<GblListTile> getAppDrawerTiles(LoginState loginState) {
    switch (loginState) {
      case LoginState.admin:
        return appDrawerTilesAdmin;
      case LoginState.basic:
        return appDrawerTilesBasic;
      default:
        return [
          const GblListTile(title: appDrawerBackToLogin, icon: Icons.arrow_back)
        ];
    }
  }

  static Future<void> getCurDir() async {
    Directory current = Directory.current;
    print("--> ${current.path}");
  }

  static Stream<ApiActionState> getInfra() async* {
    yield ApiActionState.pending;
    Future.delayed(Duration(seconds: 2), () {});
    var reply = await Api.sendGet(endpoint: ApiEndPoints.infra);
    if (reply?.body != null) {
      if ((Gbl.gblApiInfra = apiInfraFromJson(reply.body)) != null) {
        yield ApiActionState.success;
      } else {
        yield ApiActionState.fail;
      }
    } else {
      yield ApiActionState.fail;
    }
  }
}

class GblListTile {
  const GblListTile({
    this.title,
    this.icon,
  });

  final String title;
  final IconData icon;
}

//  static Future<bool> writeSharedPref(String keyVal, String val) async {
//    try {
//      SharedPreferences prf = await SharedPreferences.getInstance();
//      bool didWrite = await prf.setString(keyVal, val);
//      print("-->" + didWrite.toString());
//      return didWrite;
//    } catch (e) {
//      print("Exception [writeSharedPref]\n$e");
//    }
//    return false;
//  }
//
//  static Future<String> readSharedPref(String keyVal) async {
//    try {
//      SharedPreferences prf = await SharedPreferences.getInstance();
//      return prf.getString(keyVal);
//    } catch (e) {
//      print("Exception [readSharedPref]\n$e");
//      return null;
//    }
//  }
//

//  static Future<bool> getCurDir() async {
//    final directory = await tpp.TeTRESPathProvider.getCurrentDirectory;
//    print("------>$directory");
//    return true;
//  }
