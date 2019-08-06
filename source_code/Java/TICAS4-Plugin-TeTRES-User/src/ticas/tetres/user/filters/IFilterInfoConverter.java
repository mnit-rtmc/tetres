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

import java.util.List;
import javax.swing.JTable;
import ticas.tetres.user.types.FilterInfo;
import javax.swing.JCheckBox;

/**
 *
 * @author "Chongmyung Park <chongmyung.park@gmail.com>"
 */
public interface IFilterInfoConverter {
    public List<FilterInfo> getFilterObjects(String[][] data, boolean hasNoCondition, boolean hasAnyCondition);
    public void setFilterObjects(JTable table, JCheckBox chkNoCondition, JCheckBox chkAnyCondition, List<FilterInfo> filters);
}
