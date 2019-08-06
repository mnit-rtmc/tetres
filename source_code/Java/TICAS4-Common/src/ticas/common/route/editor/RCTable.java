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
package ticas.common.route.editor;

import java.awt.Color;
import java.awt.Component;
import java.util.List;
import javax.swing.BorderFactory;
import javax.swing.JComponent;
import javax.swing.JTable;
import javax.swing.table.DefaultTableCellRenderer;
import javax.swing.table.DefaultTableModel;
import javax.swing.table.TableCellRenderer;
import org.jdesktop.swingx.JXTable;

/**
 *
 * @author Chongmyung Park <chongmyung.park@gmail.com>
 */
public class RCTable extends JXTable {

    private List<List<CellFormat>> formats;

    public RCTable() {
    }

    public RCTable(ConfigData rci) {
        
        this.formats = rci.formats;
        
        // set data
        List<String> head = rci.rows.get(0);
        String[][] dataList = new String[rci.rows.size()][];
        for (int i = 0; i < rci.rows.size(); i++) {
            List<String> row = rci.rows.get(i);
            dataList[i] = row.toArray(new String[row.size()]);
        }
        DefaultTableModel tm = new DefaultTableModel(dataList, head.toArray(new String[head.size()]));
        this.setModel(tm);
        
        // cet center
        DefaultTableCellRenderer renderer = new DefaultTableCellRenderer() {
            @Override
            public Component getTableCellRendererComponent(JTable arg0, Object arg1, boolean arg2, boolean arg3, int arg4, int arg5) {
                Component comp = super.getTableCellRendererComponent(arg0, arg1, arg2, arg3, arg4, arg5);
                int align = DefaultTableCellRenderer.CENTER;
                ((DefaultTableCellRenderer) comp).setHorizontalAlignment(align);
                return comp;
            }
        };       
        int cols = rci.rows.get(0).size();
        for (int c = 0; c < cols; c++) {
            this.getColumnModel().getColumn(c).setCellRenderer(renderer);
        }
        
        // set border
        this.setBorder(BorderFactory.createLineBorder(Color.black));
        this.setGridColor(Color.black);
        
        // fit to content
        this.packAll();
    }

    @Override
    public Component prepareRenderer(TableCellRenderer renderer, int row, int col) {
        Component comp = super.prepareRenderer(renderer, row, col);
        Object value = getModel().getValueAt(row, col);
        comp.setForeground(Color.BLACK);
        comp.setBackground(this.formats.get(row).get(col).getColor());
        JComponent rend = (JComponent)comp;
        rend.setBorder(BorderFactory.createEmptyBorder(0, 0, 0, 0));
        return comp;
    }
}
