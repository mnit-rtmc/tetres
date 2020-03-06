package admin.sysconfig;

import admin.api.DatabasePopulationClient;
import com.google.gson.Gson;
import com.google.gson.reflect.TypeToken;
import common.pyticas.HttpResult;
import common.pyticas.IHttpResultCallback;

import javax.swing.*;
import javax.swing.border.EmptyBorder;
import java.awt.*;
import java.util.HashMap;
import java.util.Map;

public class DatabasePopulationPanel extends JPanel {
  JProgressBar progressBar;
  JPanel primaryPanel;
  JTextField trafficDataTextField;
  JTextField cadIncidentTextField;
  JTextField irisIncidentTextField;
  JTextField noaaWeatherTextField;
  JLabel trafficDataLabel;
  JLabel cadIncidentLabel;
  JLabel irisIncidentLabel;
  JLabel noaaWeatherLabel;
  JButton refreshButton;

  DatabasePopulationPanel() {
    initComponents();
  }

  private void getValuesFromServer() {
    DatabasePopulationClient client = new DatabasePopulationClient();
    client.get(new IHttpResultCallback() {
      @Override
      public void ready(HttpResult result) {
        progressBar.setVisible(false);

        Map<String, Object> retMap = new Gson().fromJson(
            result.contents, new TypeToken<HashMap<String, Object>>() {
            }.getType()
        );
        retMap.forEach((s, o) -> System.out.println("KEY: " + s + "\nOBJECT: " + o.toString()));

        Map<String, String> tdMap = new Gson().fromJson(
            retMap.get("traffic-data").toString(), new TypeToken<HashMap<String, String>>() {
            }.getType()
        );
        Map<String, String> cadMap = new Gson().fromJson(
            retMap.get("cad-incident").toString(), new TypeToken<HashMap<String, String>>() {
            }.getType()
        );
        Map<String, String> irisMap = new Gson().fromJson(
            retMap.get("iris-incident").toString(), new TypeToken<HashMap<String, String>>() {
            }.getType()
        );
        Map<String, String> noaaMap = new Gson().fromJson(
            retMap.get("noaa-weather").toString(), new TypeToken<HashMap<String, String>>() {
            }.getType()
        );


        trafficDataTextField.setText(tdMap.get("first-date") + " - " + tdMap.get("last-date"));
        noaaWeatherTextField.setText(noaaMap.get("first-date") + " - " + noaaMap.get("last-date"));
        cadIncidentTextField.setText(cadMap.get("first-date") + " - " + cadMap.get("last-date"));
        irisIncidentTextField.setText(irisMap.get("first-date") + " - " + irisMap.get("last-date"));

      }

      @Override
      public void fail(HttpResult result) {
        System.out.println(result.contents);
        progressBar.setVisible(false);
      }
    });
  }

  private void initComponents() {
    primaryPanel = new JPanel();
    primaryPanel.setLayout(new GridLayout(5, 2));
    primaryPanel.setBorder(new EmptyBorder(10, 10, 10, 10));


    trafficDataTextField = new JTextField();
    cadIncidentTextField = new JTextField();
    irisIncidentTextField = new JTextField();
    noaaWeatherTextField = new JTextField();

    trafficDataLabel = new JLabel();
    cadIncidentLabel = new JLabel();
    irisIncidentLabel = new JLabel();
    noaaWeatherLabel = new JLabel();

    refreshButton = new JButton();
    refreshButton.setText("Refresh");
    refreshButton.addActionListener(e -> getValuesFromServer());

    trafficDataLabel.setText("Traffic Data");
    cadIncidentLabel.setText("Cad Incident");
    irisIncidentLabel.setText("Iris Incident");
    noaaWeatherLabel.setText("NOAA Weather");
    trafficDataTextField.setEditable(false);
    cadIncidentTextField.setEditable(false);
    irisIncidentTextField.setEditable(false);
    noaaWeatherTextField.setEditable(false);

    primaryPanel.add(trafficDataLabel);
    primaryPanel.add(trafficDataTextField);
    primaryPanel.add(cadIncidentLabel);
    primaryPanel.add(cadIncidentTextField);
    primaryPanel.add(irisIncidentLabel);
    primaryPanel.add(irisIncidentTextField);
    primaryPanel.add(noaaWeatherLabel);
    primaryPanel.add(noaaWeatherTextField);


    progressBar = new JProgressBar();
    progressBar.setVisible(false);
    progressBar.setIndeterminate(true);
    primaryPanel.add(progressBar);


    this.setLayout(new GridLayout(2, 2));
    this.add(primaryPanel);
    this.add(new JLabel());
    this.add(new JLabel());
    this.add(refreshButton);

  }
}
