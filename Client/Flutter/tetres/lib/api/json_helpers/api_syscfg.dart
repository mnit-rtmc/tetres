import 'dart:convert';

ApiSyscfg apiSyscfgFromJson(String str) => ApiSyscfg.fromJson(json.decode(str));

String apiSyscfgToJson(ApiSyscfg data) => json.encode(data.toJson());

class ApiSyscfg {
  int code;
  String message;
  ApiSyscfgObj obj;

  ApiSyscfg({
    this.code,
    this.message,
    this.obj,
  });

  factory ApiSyscfg.fromJson(Map<String, dynamic> json) => ApiSyscfg(
        code: json["code"],
        message: json["message"],
        obj: ApiSyscfgObj.fromJson(json["obj"]),
      );

  Map<String, dynamic> toJson() => {
        "code": code,
        "message": message,
        "obj": obj.toJson(),
      };
}

class ApiSyscfgObj {
  String objClass;
  String module;
  int dataArchiveStartYear;
  String dailyJobStartTime;
  int dailyJobOffsetDays;
  String weeklyJobStartDay;
  String weeklyJobStartTime;
  int monthlyJobStartDate;
  String monthlyJobStartTime;
  int incidentDownstreamDistanceLimit;
  int incidentUpstreamDistanceLimit;
  int workzoneDownstreamDistanceLimit;
  int workzoneUpstreamDistanceLimit;
  int specialeventArrivalWindow;
  int specialeventDepartureWindow1;
  int specialeventDepartureWindow2;

  ApiSyscfgObj({
    this.objClass,
    this.module,
    this.dataArchiveStartYear,
    this.dailyJobStartTime,
    this.dailyJobOffsetDays,
    this.weeklyJobStartDay,
    this.weeklyJobStartTime,
    this.monthlyJobStartDate,
    this.monthlyJobStartTime,
    this.incidentDownstreamDistanceLimit,
    this.incidentUpstreamDistanceLimit,
    this.workzoneDownstreamDistanceLimit,
    this.workzoneUpstreamDistanceLimit,
    this.specialeventArrivalWindow,
    this.specialeventDepartureWindow1,
    this.specialeventDepartureWindow2,
  });

  factory ApiSyscfgObj.fromJson(Map<String, dynamic> json) {
    try {
      return ApiSyscfgObj(
        objClass: json["__class__"],
        module: json["__module__"],
        dataArchiveStartYear: json["data_archive_start_year"],
        dailyJobStartTime: json["daily_job_start_time"],
        dailyJobOffsetDays: json["daily_job_offset_days"],
        weeklyJobStartDay: json["weekly_job_start_day"],
        weeklyJobStartTime: json["weekly_job_start_time"],
        monthlyJobStartDate: json["monthly_job_start_date"],
        monthlyJobStartTime: json["monthly_job_start_time"],
        incidentDownstreamDistanceLimit:
            json["incident_downstream_distance_limit"],
        incidentUpstreamDistanceLimit: json["incident_upstream_distance_limit"],
        workzoneDownstreamDistanceLimit:
            json["workzone_downstream_distance_limit"],
        workzoneUpstreamDistanceLimit: json["workzone_upstream_distance_limit"],
        specialeventArrivalWindow: json["specialevent_arrival_window"],
        specialeventDepartureWindow1: json["specialevent_departure_window1"],
        specialeventDepartureWindow2: json["specialevent_departure_window2"],
      );
    } catch (e) {
      print(e);
    }
    return null;
  }

  Map<String, dynamic> toJson() => {
        "__class__": objClass,
        "__module__": module,
        "data_archive_start_year": dataArchiveStartYear,
        "daily_job_start_time": dailyJobStartTime,
        "daily_job_offset_days": dailyJobOffsetDays,
        "weekly_job_start_day": weeklyJobStartDay,
        "weekly_job_start_time": weeklyJobStartTime,
        "monthly_job_start_date": monthlyJobStartDate,
        "monthly_job_start_time": monthlyJobStartTime,
        "incident_downstream_distance_limit": incidentDownstreamDistanceLimit,
        "incident_upstream_distance_limit": incidentUpstreamDistanceLimit,
        "workzone_downstream_distance_limit": workzoneDownstreamDistanceLimit,
        "workzone_upstream_distance_limit": workzoneUpstreamDistanceLimit,
        "specialevent_arrival_window": specialeventArrivalWindow,
        "specialevent_departure_window1": specialeventDepartureWindow1,
        "specialevent_departure_window2": specialeventDepartureWindow2,
      };
}
