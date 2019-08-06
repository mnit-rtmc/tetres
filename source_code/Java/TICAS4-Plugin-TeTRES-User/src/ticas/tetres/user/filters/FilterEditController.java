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
package ticas.tetres.user.filters;

import ticas.tetres.user.TeTRESConfig;
import java.awt.event.ActionEvent;
import java.util.List;
import javax.swing.JButton;
import javax.swing.JOptionPane;
import javax.swing.JTable;
import javax.swing.table.DefaultTableModel;
import ticas.tetres.user.types.FilterInfo;
import ticas.tetres.user.types.WeatherConditionInfo;
import java.awt.event.ActionListener;
import javax.swing.JCheckBox;

/**
 *
 * @author "Chongmyung Park <chongmyung.park@gmail.com>"
 */
public final class FilterEditController {

    private final FilterEditDialog dialog;
    private final JTable table;
    private final JButton btnAdd;
    private final JButton btnDelete;
    private final IFilterInfoConverter filterInfoConverter;
    private boolean isChanged = false;
    private final JCheckBox chkNoCondition;
    private final JCheckBox chkAnyCondition;
    
    public FilterEditController(FilterEditDialog dialog, JTable table, JButton btnAdd, JButton btnDelete, 
            JCheckBox chkNoCondition, JCheckBox chkAnyCondition, IFilterInfoConverter filterInfoConverter) {
        this.dialog = dialog;
        this.table = table;
        this.btnAdd = btnAdd;
        this.btnDelete = btnDelete;
        this.chkNoCondition = chkNoCondition;
        this.chkAnyCondition = chkAnyCondition;
        this.filterInfoConverter = filterInfoConverter;
        this.chkNoCondition.addActionListener(new ActionListener() {
            @Override
            public void actionPerformed(ActionEvent ae) {
                isChanged = true;
            }
        });
        this.chkAnyCondition.addActionListener(new ActionListener() {
            @Override
            public void actionPerformed(ActionEvent ae) {
                isChanged = true;
            }
        });        
        this.init();
    }
       
    public void setEnabled(boolean v)
    {
        if(this.btnAdd != null) {
            this.btnAdd.setEnabled(v);
        }
        if(this.btnDelete != null) {
            this.btnDelete.setEnabled(v);
        }
    }

    public void init() {
        if(this.dialog != null) {
            this.dialog.setDataTable(this.table);
        }
        
        if(this.btnAdd != null) {
            this.btnAdd.addActionListener(this::add);
        }
        
        if(this.btnDelete != null) {
            this.btnDelete.addActionListener(this::delete);
        }
    }

    public void add(ActionEvent evt) {
        if(this.dialog == null) return;        
        this.dialog.reset();
        this.dialog.setVisible(true);
        if(this.dialog.isDirty()) {
            this.isChanged = true;
            if(this.chkAnyCondition != null) {
                this.chkAnyCondition.setSelected(false);
            }
            if(this.chkNoCondition != null) {
                this.chkNoCondition.setSelected(false);
            }
        }
    }
    
    public boolean isDirty() {
        return this.isChanged;
    }

    public void delete(ActionEvent evt) {
        if(this.table == null) return;
        
        int[] rows = table.getSelectedRows();
        if(rows.length == 0) {
            JOptionPane.showMessageDialog(this.dialog, "Select items first");
            return;
        }
        if (JOptionPane.showConfirmDialog(this.dialog, "Delete the selected items?", "Confirm", JOptionPane.YES_NO_OPTION) != JOptionPane.YES_OPTION) {
            return;
        }
        DefaultTableModel model = (DefaultTableModel) this.table.getModel();
        
        for (int i = 0; i < rows.length; i++) {
            model.removeRow(rows[i] - i);
        }
        this.isChanged = true;
    }
    
    public void reset() {
        if(this.table != null) {
            DefaultTableModel model = (DefaultTableModel) this.table.getModel();        
            model.setRowCount(0);
        }
        this.chkNoCondition.setSelected(true);
        this.chkAnyCondition.setSelected(false);
        this.isChanged = false;
    }

    public List getFilterObjects() {
        return this.filterInfoConverter.getFilterObjects(this.getTableData(this.table), 
                this.chkNoCondition.isSelected(), this.chkAnyCondition.isSelected());
    }

    private String[][] getTableData(JTable table) {
        if(table == null) {
            return null;
        }
        DefaultTableModel dtm = (DefaultTableModel) table.getModel();
        int nRow = dtm.getRowCount(), nCol = dtm.getColumnCount();
        String[][] tableData = new String[nRow][nCol];
        for (int i = 0; i < nRow; i++) {
            for (int j = 0; j < nCol; j++) {
                tableData[i][j] = dtm.getValueAt(i, j).toString();
            }
        }
        return tableData;
    }

    public void setFilter(List filterInfos) {
        this.filterInfoConverter.setFilterObjects(this.table, this.chkNoCondition, this.chkAnyCondition, filterInfos);
    }
}
