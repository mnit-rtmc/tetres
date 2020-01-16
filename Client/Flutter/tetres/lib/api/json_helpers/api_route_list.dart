import 'dart:convert';

ApiRouteList apiRouteListFromJson(String str) => ApiRouteList.fromJson(json.decode(str));

String apiRouteListToJson(ApiRouteList data) => json.encode(data.toJson());

class ApiRouteList {
  int code;
  String message;
  ApiRouteListObj obj;

  ApiRouteList({
    this.code,
    this.message,
    this.obj,
  });

  factory ApiRouteList.fromJson(Map<String, dynamic> json) => ApiRouteList(
    code: json["code"],
    message: json["message"],
    obj: ApiRouteListObj.fromJson(json["obj"]),
  );

  Map<String, dynamic> toJson() => {
    "code": code,
    "message": message,
    "obj": obj.toJson(),
  };
}

class ApiRouteListObj {
  List<ApiRouteListElement> list;

  ApiRouteListObj({
    this.list,
  });

  factory ApiRouteListObj.fromJson(Map<String, dynamic> json) => ApiRouteListObj(
    list: List<ApiRouteListElement>.from(json["list"].map((x) => ApiRouteListElement.fromJson(x))),
  );

  Map<String, dynamic> toJson() => {
    "list": List<dynamic>.from(list.map((x) => x.toJson())),
  };
}

class ApiRouteListElement {
  String listClass;
  String module;
  int id;
  String name;
  String corridor;
  String description;
  ApiRouteListRoute route;
  RegDate regDate;

  ApiRouteListElement({
    this.listClass,
    this.module,
    this.id,
    this.name,
    this.corridor,
    this.description,
    this.route,
    this.regDate,
  });

  factory ApiRouteListElement.fromJson(Map<String, dynamic> json) => ApiRouteListElement(
    listClass: json["__class__"],
    module: json["__module__"],
    id: json["id"],
    name: json["name"],
    corridor: json["corridor"],
    description: json["description"],
    route: ApiRouteListRoute.fromJson(json["route"]),
    regDate: RegDate.fromJson(json["reg_date"]),
  );

  Map<String, dynamic> toJson() => {
    "__class__": listClass,
    "__module__": module,
    "id": id,
    "name": name,
    "corridor": corridor,
    "description": description,
    "route": route.toJson(),
    "reg_date": regDate.toJson(),
  };
}

class RegDate {
  String type;
  DateTime datetime;

  RegDate({
    this.type,
    this.datetime,
  });

  factory RegDate.fromJson(Map<String, dynamic> json) => RegDate(
    type: json["__type__"],
    datetime: DateTime.parse(json["datetime"]),
  );

  Map<String, dynamic> toJson() => {
    "__type__": type,
    "datetime": datetime.toIso8601String(),
  };
}

class ApiRouteListRoute {
  String routeClass;
  String module;
  String name;
  String desc;
  dynamic infraCfgDate;
  List<String> rnodes;
  dynamic cfg;

  ApiRouteListRoute({
    this.routeClass,
    this.module,
    this.name,
    this.desc,
    this.infraCfgDate,
    this.rnodes,
    this.cfg,
  });

  factory ApiRouteListRoute.fromJson(Map<String, dynamic> json) => ApiRouteListRoute(
    routeClass: json["__class__"],
    module: json["__module__"],
    name: json["name"],
    desc: json["desc"],
    infraCfgDate: json["infra_cfg_date"],
    rnodes: List<String>.from(json["rnodes"].map((x) => x)),
    cfg: json["cfg"],
  );

  Map<String, dynamic> toJson() => {
    "__class__": routeClass,
    "__module__": module,
    "name": name,
    "desc": desc,
    "infra_cfg_date": infraCfgDate,
    "rnodes": List<dynamic>.from(rnodes.map((x) => x)),
    "cfg": cfg,
  };
}
