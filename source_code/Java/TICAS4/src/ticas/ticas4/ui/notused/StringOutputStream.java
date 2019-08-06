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

package ticas.ticas4.ui.notused;

import java.io.IOException;
import java.io.OutputStream;
import javax.swing.JTextArea;

/**
 *
 * @author Chongmyung Park <chongmyung.park@gmail.com>
 */
public class StringOutputStream extends OutputStream {

    JTextArea targetTextBox;
    StringBuilder message = new StringBuilder();
    
    public StringOutputStream(JTextArea tbx) {
        this.targetTextBox = tbx;
    }       

    @Override
    public void write(int b) throws IOException {
        message.append((char) b);
        targetTextBox.setText(message.toString());
        targetTextBox.setCaretPosition(targetTextBox.getDocument().getLength());
    }
}
