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

import javax.swing.JTable;

/**
 *
 * @author "Chongmyung Park <chongmyung.park@gmail.com>"
 */
public abstract class FilterEditDialog extends javax.swing.JDialog  {

    protected JTable table;
    protected boolean isChanged;
    
    /**
     * Creates new form WeatherEditDialog
     */
    public FilterEditDialog(java.awt.Frame parent, boolean modal) {
        super(parent, modal);
    }    

    public void setDataTable(JTable table) {
        this.table = table;
    }
    
    public boolean isDirty() {
        return this.isChanged;
    }
    
    abstract public void reset();
    abstract public void updateDataTable();
}
