package admin.types;

import com.google.gson.Gson;
import com.google.gson.GsonBuilder;

import java.util.Map;

public class DatabasePopulationInfo extends InfoBase {

  public Map<String, Map<String, String>> traffic_data;
  public Map<String, Map<String, String>> cad_incident;
  public Map<String, Map<String, String>> iris_incident;
  public Map<String, Map<String, String>> noaa_weather;

  public DatabasePopulationInfo() {
  }

  @Override
  public DatabasePopulationInfo clone() {
    Gson gson = new GsonBuilder().create();
    String json = gson.toJson(this);
    return gson.fromJson(json, DatabasePopulationInfo.class);
  }
}
