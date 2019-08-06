/*
 * Copyright (C) 2018 NATSRL @ UMD (University Minnesota Duluth)
 * 
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program.  If not, see <http://www.gnu.org/licenses/>.
 */
package ticas.common.config.ui;

import ticas.common.util.FileHelper;
import ticas.common.util.FormHelper;
import java.awt.BorderLayout;
import java.awt.Dimension;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;
import java.util.List;
import javax.swing.BorderFactory;
import javax.swing.BoxLayout;
import javax.swing.JButton;
import javax.swing.JCheckBox;
import javax.swing.JComboBox;
import javax.swing.JLabel;
import javax.swing.JPanel;
import javax.swing.JRadioButton;
import javax.swing.JScrollPane;
import javax.swing.JTextArea;
import javax.swing.border.Border;

/**
 *
 * @author Chongmyung Park <chongmyung.park@gmail.com>
 */
public class ConfigItem extends javax.swing.JPanel {

    private final Object defaultValue;
    private final ConfigType cfgType;
    private final String label;
    private JTextArea inputField;
    private JComboBox checkField;
    private List<Object> choices = null;

    /**
     * Creates new form ConfigItem
     */
    public ConfigItem(String label, Object defaultValue, ConfigType cfgType) {
        this(label, defaultValue, null, cfgType);
    }
    
    public ConfigItem(String label, Object defaultValue, List<Object> choices, ConfigType cfgType) {
        initComponents();
        this.label = label;
        this.defaultValue = defaultValue;
        this.cfgType = cfgType;
        this.setLayout(new BorderLayout());
        this.setMaximumSize(new Dimension(Integer.MAX_VALUE, 50));
        this.choices = choices;          
        
        this.init();
    }    

    public void init() {

        // add label
        JLabel lbName = new JLabel(label);
        Border paddingBorder = BorderFactory.createEmptyBorder(15, 0, 0, 0);
        Border border = BorderFactory.createEmptyBorder();
        lbName.setBorder(BorderFactory.createCompoundBorder(border, paddingBorder));
        this.add(lbName, BorderLayout.PAGE_START);

        // add input panel
        JPanel inputPanel = new JPanel();
        inputPanel.setLayout(new BoxLayout(inputPanel, BoxLayout.LINE_AXIS));
        
        if(this.choices != null) {
            checkField = new JComboBox();
            int slt = 0;
            int idx = 0;
            for(Object obj : choices) {
                checkField.addItem(obj);
                if(obj.equals(defaultValue)) {
                    slt = idx;
                }
                idx ++;
            }
            checkField.setSelectedIndex(slt);
            inputPanel.add(checkField);              
        }
        else if (ConfigType.BOOLEAN.equals(cfgType)) {
            checkField = new JComboBox();
            checkField.addItem("True");
            checkField.addItem("False");
            if ((boolean) defaultValue == true) {
                checkField.setSelectedIndex(0);
            } else {
                checkField.setSelectedIndex(1);
            }

            inputPanel.add(checkField);                     
        } else {
            // create text area
            inputField = new JTextArea();
            inputField.setText(defaultValue.toString());
            if (ConfigType.DOUBLE.equals(cfgType)) {
                FormHelper.setDoubleFilter(inputField.getDocument(), true);
            } else if (ConfigType.INTEGER.equals(cfgType)) {
                FormHelper.setIntegerFilter(inputField.getDocument(), true);
            } 

            inputPanel.add(inputField);

            // for file
            if (ConfigType.FILE.equals(cfgType)) {
                JButton btnBrowseFile = new JButton("Browse");
                btnBrowseFile.addActionListener(new ActionListener() {
                    @Override
                    public void actionPerformed(ActionEvent e) {
                        String filepath = FileHelper.chooseFileToOpen(FileHelper.currentPath(), "Select File");
                        if (filepath != null && !filepath.isEmpty()) {
                            inputField.setText(filepath);
                        }
                    }
                });
                inputPanel.add(btnBrowseFile);
                // for directory
            } else if (ConfigType.DIRECTORY.equals(cfgType)) {
                JButton btnBrowseFile = new JButton("Browse");
                btnBrowseFile.addActionListener(new ActionListener() {
                    @Override
                    public void actionPerformed(ActionEvent e) {
                        String filepath = FileHelper.chooseDirectory(FileHelper.currentPath(), "Select Directory");
                        if (filepath != null && !filepath.isEmpty()) {
                            inputField.setText(filepath);
                        }
                    }
                });
                inputPanel.add(btnBrowseFile);
            }
        }

        this.add(inputPanel, BorderLayout.CENTER);
    }

    public String getStringValue() {
        if(this.checkField != null) return this.checkField.getSelectedItem().toString();
        return inputField.getText();
    }

    public Integer getIntegerValue() {
        if(this.checkField != null) return FormHelper.getInteger(this.checkField.getSelectedItem().toString());
        return FormHelper.getInteger(this.inputField.getText());
    }

    public Double getDoubleValue() {
        if(this.checkField != null) return FormHelper.getDouble(this.checkField.getSelectedItem().toString());
        return FormHelper.getDouble(this.inputField.getText());
    }

    public List<Double> getDoubleListValue() {
        if(this.checkField != null) return FormHelper.getDoubleList(this.checkField.getSelectedItem().toString());
        return FormHelper.getDoubleList(this.inputField.getText());
    }

    public List<Integer> getIntegerListValue() {
        if(this.checkField != null) return FormHelper.getIntegerList(this.checkField.getSelectedItem().toString());
        return FormHelper.getIntegerList(this.inputField.getText());
    }

    public Boolean getBooleanValue() {
        return (Boolean.parseBoolean(this.checkField.getSelectedItem().toString()));
    }

    /**
     * This method is called from within the constructor to initialize the form.
     * WARNING: Do NOT modify this code. The content of this method is always
     * regenerated by the Form Editor.
     */
    @SuppressWarnings("unchecked")
    // <editor-fold defaultstate="collapsed" desc="Generated Code">//GEN-BEGIN:initComponents
    private void initComponents() {

        javax.swing.GroupLayout layout = new javax.swing.GroupLayout(this);
        this.setLayout(layout);
        layout.setHorizontalGroup(
            layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
            .addGap(0, 710, Short.MAX_VALUE)
        );
        layout.setVerticalGroup(
            layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
            .addGap(0, 435, Short.MAX_VALUE)
        );
    }// </editor-fold>//GEN-END:initComponents


    // Variables declaration - do not modify//GEN-BEGIN:variables
    // End of variables declaration//GEN-END:variables
}
