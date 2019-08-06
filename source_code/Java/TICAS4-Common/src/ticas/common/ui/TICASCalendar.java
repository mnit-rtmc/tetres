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
package ticas.common.ui;

import java.awt.Font;
import java.awt.GridLayout;
import java.awt.Insets;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;
import java.text.SimpleDateFormat;
import java.util.Calendar;
import java.util.Date;
import java.util.EventObject;
import java.util.GregorianCalendar;
import java.util.TreeSet;

import javax.swing.JLabel;
import javax.swing.JToggleButton;

/**
 *
 * @author Chongmyung Park <chongmyung.park@gmail.com>
 */
public final class TICASCalendar extends javax.swing.JPanel {
    
    /** default DateChecker - return true always */
    private IDateChecker dateChecker = new IDateChecker() {
        @Override
        public boolean isAvailable(Calendar c) {
            return true;
        }
        @Override
        public boolean isAvailable(Date d) {
            return true;
        }
    };
    
    /**
     * button Toggle Iistener
     */
    private DayToggleListener daybuttonListener;

    /** Creates new form TICASCalendar */
    public TICASCalendar() {
        initComponents();
        createButtonGrid();
        bindEvent();
        initialize();
    }
    
    static protected final SimpleDateFormat formatter = new SimpleDateFormat("MMM, yyyy");
    static public final int DATE_ADDED = 1;
    static public final int DATE_REMOVED = 2;
    protected final Calendar month = Calendar.getInstance();
    protected final JLabel[] spacer = new JLabel[8];
    protected final JToggleButton dayButton[] = new JToggleButton[31];
    protected final TreeSet<Date> selected = new TreeSet<Date>();
    protected int maxSelectedDays = 300;
    protected Listener listeners;

    /** Get the current selection set */
    public Calendar[] getSelectedDates() {
        Calendar[] result = new Calendar[selected.size()];
        int i = 0;
        for (Date d : selected) {
            Calendar c = Calendar.getInstance();
            c.setTime(d);
            result[i++] = c;
        }

        return result;
    }

    /** Select calendar dates at startup */
    public void preselectDate(Calendar c) {
        while (month.get(Calendar.YEAR) != c.get(Calendar.YEAR)) {
            if (month.get(Calendar.YEAR) > c.get(Calendar.YEAR)) {
                this.btnPrevYear.doClick();
            } else {
                this.btnNextYear.doClick();
            }
        }
        while (month.get(Calendar.MONTH) != c.get(Calendar.MONTH)) {
            if (month.get(Calendar.MONTH) > c.get(Calendar.MONTH)) {
                this.btnPrevMonth.doClick();
            } else {
                this.btnNextMonth.doClick();
            }
        }
        JToggleButton tempButton = dayButton[c.get(Calendar.DAY_OF_MONTH) - 1];
        tempButton.doClick();
    }
    
    public void setMonth(Calendar m) {        
        this.month.set(Calendar.YEAR, m.get(Calendar.YEAR));
        this.month.set(Calendar.MONTH, m.get(Calendar.MONTH));
        initialize();
    }

    /** Set the maximum number of selected days */
    public void setMaxSelectedDays(int m) {
        maxSelectedDays = m;
        if (selected.size() >= maxSelectedDays) {
            disableMoreSelections();
        } else {
            enableMoreSelections();
        }
    }

    protected void createButtonGrid() {
        GridLayout grid = new GridLayout(0, 7);
        panCalendar.setLayout(grid);

        Font font = new java.awt.Font("Verdana", 0, 9);
        JLabel sun = new JLabel("S", JLabel.CENTER);
        JLabel mon = new JLabel("M", JLabel.CENTER);
        JLabel tue = new JLabel("Tu", JLabel.CENTER);
        JLabel wed = new JLabel("W", JLabel.CENTER);
        JLabel thu = new JLabel("Th", JLabel.CENTER);
        JLabel fri = new JLabel("F", JLabel.CENTER);
        JLabel sat = new JLabel("S", JLabel.CENTER);
        sun.setFont(font);
        mon.setFont(font);
        tue.setFont(font);
        wed.setFont(font);
        thu.setFont(font);
        fri.setFont(font);
        sat.setFont(font);
        panCalendar.add(sun);
        panCalendar.add(mon);
        panCalendar.add(tue);
        panCalendar.add(wed);
        panCalendar.add(thu);
        panCalendar.add(fri);
        panCalendar.add(sat);

        for (int s = 0; s < 8; s++) {
            spacer[s] = new JLabel();
        }

        for (int d = 0; d < 31; d++) {
            final int day = d + 1;
            final JToggleButton b = new JToggleButton(String.valueOf(day));
            b.setMargin(new Insets(1, 1, 1, 1));
            b.setFont(font); // NOI18N
            dayButton[d] = b;
            dayButton[d].addActionListener(new ActionListener() {

                public void actionPerformed(ActionEvent e) {
                    dayButtonToggled(b, day);
                }
            });
        }
    }

    protected void initialize() {
        lbYear.setText(formatter.format(month.getTime()));

        for (int s = 0; s < 8; s++) {
            panCalendar.remove(spacer[s]);
        }
        for (int day = 0; day < 31; day++) {
            panCalendar.remove(dayButton[day]);
            dayButton[day].setSelected(false);
        }
        panCalendar.revalidate();
        int y = month.get(Calendar.YEAR);
        int m = month.get(Calendar.MONTH);

        Calendar c = Calendar.getInstance();

        for (Date d : selected) {
            c.setTime(d);
            if (c.get(Calendar.YEAR) == y) {
                if (c.get(Calendar.MONTH) == m) {
                    int day = c.get(Calendar.DATE) - 1;
                    dayButton[day].setSelected(true);
                }
            }
        }

        if (selected.size() < maxSelectedDays) {
            enableMoreSelections();
        } else {
            disableMoreSelections();
        }
        int skip = month.get(Calendar.DAY_OF_WEEK) - 1;

        for (int s = 0; s < skip; s++) {
            panCalendar.add(spacer[s]);
        }
        for (int day = 0; day < month.getActualMaximum(Calendar.DATE); day++) {
            panCalendar.add(dayButton[day]);
        }
        for (int s = skip; s < 8; s++) {
            panCalendar.add(spacer[s]);
        }

        panCalendar.repaint();
    }

    protected void dayButtonToggled(JToggleButton button, int day) {
        int y = month.get(Calendar.YEAR);
        int m = month.get(Calendar.MONTH);
        GregorianCalendar calendar = new GregorianCalendar(y, m, day, 0, 0, 0);
        
        if (button.isSelected()) {
            selected.add(calendar.getTime());
            if (selected.size() >= maxSelectedDays) {
                disableMoreSelections();
            }
            processDateAddedEvent(calendar);
        } else {
            selected.remove(calendar.getTime());
            if (selected.size() < maxSelectedDays) {
                enableMoreSelections();
            }
            processDateRemovedEvent(calendar);
        }
        
        if(daybuttonListener != null){
            daybuttonListener.onButtonToggle(button.isSelected(), day);
        }
    }

    protected void enableMoreSelections() {
        int y = month.get(Calendar.YEAR);
        int m = month.get(Calendar.MONTH);
        GregorianCalendar c =
                new GregorianCalendar(y, m, 1, 0, 0, 0);


        for (int d = 0; d < 31; d++) {
            c.set(Calendar.DAY_OF_MONTH, d + 1);

            dayButton[ d ].setEnabled(dateChecker.isAvailable(c));
        }
    }

    protected void disableMoreSelections() {
        int y = month.get(Calendar.YEAR);
        int m = month.get(Calendar.MONTH);
        GregorianCalendar c =
                new GregorianCalendar(y, m, 1, 0, 0, 0);

        for (int d = 0; d < 31; d++) {
            if (dayButton[d].isSelected()) {
                c.set(Calendar.DAY_OF_MONTH, d + 1);
                dayButton[ d ].setEnabled(dateChecker.isAvailable(c));
            } else {
                dayButton[d].setEnabled(false);
            }
        }
    }

    /** Process a "date added" event */
    protected void processDateAddedEvent(Calendar c) {
        if (listeners != null) {
            Event e = new Event(this, DATE_ADDED, c);
            listeners.dateAdded(e);
        }
    }

    /** Process a "date removed" event */
    protected void processDateRemovedEvent(Calendar c) {
        if (listeners != null) {
            Event e = new Event(this, DATE_REMOVED, c);
            listeners.dateRemoved(e);
        }
    }

    protected Listener add(Listener a, Listener b) {
        if (a == null) {
            return b;
        }
        if (b == null) {
            return a;
        }
        return new EventMulticaster(a, b);
    }

    protected static Listener remove(Listener l, Listener old) {
        if (l == null || l == old) {
            return null;
        }
        if (l instanceof EventMulticaster) {
            return ((EventMulticaster) l).remove(old);
        }
        return l;
    }

    private void bindEvent() {
        month.set(Calendar.DAY_OF_MONTH, 1);
        this.btnPrevYear.addActionListener(new ActionListener() {

            public void actionPerformed(ActionEvent e) {
                month.add(Calendar.YEAR, -1);
                initialize();
            }
        });
        this.btnPrevMonth.addActionListener(new ActionListener() {

            public void actionPerformed(ActionEvent e) {
                month.add(Calendar.MONTH, -1);
                initialize();
            }
        });
        this.btnNextMonth.addActionListener(new ActionListener() {

            public void actionPerformed(ActionEvent e) {
                month.add(Calendar.MONTH, 1);
                initialize();
            }
        });
        this.btnNextYear.addActionListener(new ActionListener() {

            public void actionPerformed(ActionEvent e) {
                month.add(Calendar.YEAR, 1);
                initialize();
            }
        });
        this.btnClear.addActionListener(new ActionListener() {

            public void actionPerformed(ActionEvent e) {
                clearAll();
            }
        });
    }

    public void clearAll() {
        Calendar c = Calendar.getInstance();
        for (Date d : selected) {
            c.setTime(d);
            processDateRemovedEvent(c);
        }
        selected.clear();

        initialize();
    }

    public void setDateChecker(IDateChecker dc) {
        this.dateChecker = dc;
        this.initialize();
    }
    
    public void setDayToggleListener(DayToggleListener listener){
        this.daybuttonListener = listener;
    }

    public class Event extends EventObject {

        protected final int type;

        public int getType() {
            return type;
        }
        protected final Calendar calendar;

        public Date getDate() {
            return calendar.getTime();
        }

        protected Event(TICASCalendar source, int t, Calendar c) {
            super(source);
            type = t;
            calendar = c;
        }
    }

    public interface Listener {

        public void dateAdded(Event e);

        public void dateRemoved(Event e);
    }

    protected class EventMulticaster implements Listener {

        protected final Listener a;
        protected final Listener b;

        protected EventMulticaster(Listener a, Listener b) {
            this.a = a;
            this.b = b;
        }

        protected Listener remove(Listener l) {
            if (l == a) {
                return b;
            }
            if (l == b) {
                return a;
            }
            Listener newA = TICASCalendar.remove(a, l);
            Listener newB = TICASCalendar.remove(b, l);
            if (newA == a && newB == b) {
                return this;
            }
            return add(newA, newB);
        }

        public void dateAdded(Event e) {
            a.dateAdded(e);
            b.dateAdded(e);
        }

        public void dateRemoved(Event e) {
            a.dateRemoved(e);
            b.dateRemoved(e);
        }
    }

    /** This method is called from within the constructor to
     * initialize the form.
     * WARNING: Do NOT modify this code. The content of this method is
     * always regenerated by the Form Editor.
     */
    @SuppressWarnings("unchecked")
    // <editor-fold defaultstate="collapsed" desc="Generated Code">//GEN-BEGIN:initComponents
    private void initComponents() {

        panToolbar = new javax.swing.JPanel();
        btnPrevYear = new javax.swing.JButton();
        btnPrevMonth = new javax.swing.JButton();
        lbYear = new javax.swing.JLabel();
        btnNextYear = new javax.swing.JButton();
        btnNextMonth = new javax.swing.JButton();
        btnClear = new javax.swing.JButton();
        panCalendar = new javax.swing.JPanel();

        btnPrevYear.setFont(new java.awt.Font("Verdana", 0, 9)); // NOI18N
        btnPrevYear.setText("<<");
        btnPrevYear.setMargin(new java.awt.Insets(1, 1, 1, 1));
        btnPrevYear.addActionListener(new java.awt.event.ActionListener() {
            public void actionPerformed(java.awt.event.ActionEvent evt) {
                btnPrevYearActionPerformed(evt);
            }
        });

        btnPrevMonth.setFont(new java.awt.Font("Verdana", 0, 9)); // NOI18N
        btnPrevMonth.setText("<");
        btnPrevMonth.setMargin(new java.awt.Insets(1, 1, 1, 1));

        lbYear.setFont(new java.awt.Font("Tahoma", 0, 10)); // NOI18N
        lbYear.setHorizontalAlignment(javax.swing.SwingConstants.CENTER);
        lbYear.setText("Year");
        lbYear.setPreferredSize(new java.awt.Dimension(50, 13));

        btnNextYear.setFont(new java.awt.Font("Verdana", 0, 9)); // NOI18N
        btnNextYear.setText(">>");
        btnNextYear.setMargin(new java.awt.Insets(1, 1, 1, 1));

        btnNextMonth.setFont(new java.awt.Font("Verdana", 0, 9)); // NOI18N
        btnNextMonth.setText(">");
        btnNextMonth.setMargin(new java.awt.Insets(1, 1, 1, 1));

        btnClear.setFont(new java.awt.Font("Verdana", 0, 9)); // NOI18N
        btnClear.setText("Clear");
        btnClear.setMargin(new java.awt.Insets(1, 1, 1, 1));

        javax.swing.GroupLayout panToolbarLayout = new javax.swing.GroupLayout(panToolbar);
        panToolbar.setLayout(panToolbarLayout);
        panToolbarLayout.setHorizontalGroup(
            panToolbarLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
            .addGroup(javax.swing.GroupLayout.Alignment.TRAILING, panToolbarLayout.createSequentialGroup()
                .addComponent(btnPrevYear, javax.swing.GroupLayout.DEFAULT_SIZE, 24, Short.MAX_VALUE)
                .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.RELATED)
                .addComponent(btnPrevMonth, javax.swing.GroupLayout.DEFAULT_SIZE, 24, Short.MAX_VALUE)
                .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.RELATED)
                .addComponent(lbYear, javax.swing.GroupLayout.DEFAULT_SIZE, 55, Short.MAX_VALUE)
                .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.RELATED)
                .addComponent(btnNextMonth, javax.swing.GroupLayout.DEFAULT_SIZE, 26, Short.MAX_VALUE)
                .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.RELATED)
                .addComponent(btnNextYear, javax.swing.GroupLayout.DEFAULT_SIZE, 32, Short.MAX_VALUE)
                .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.RELATED)
                .addComponent(btnClear, javax.swing.GroupLayout.DEFAULT_SIZE, 44, Short.MAX_VALUE)
                .addContainerGap())
        );
        panToolbarLayout.setVerticalGroup(
            panToolbarLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
            .addGroup(panToolbarLayout.createSequentialGroup()
                .addGroup(panToolbarLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.BASELINE)
                    .addComponent(btnPrevYear, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, Short.MAX_VALUE)
                    .addComponent(btnPrevMonth, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, Short.MAX_VALUE)
                    .addComponent(lbYear, javax.swing.GroupLayout.PREFERRED_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.PREFERRED_SIZE)
                    .addComponent(btnNextMonth, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, Short.MAX_VALUE)
                    .addComponent(btnNextYear, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, Short.MAX_VALUE)
                    .addComponent(btnClear, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, Short.MAX_VALUE))
                .addContainerGap(javax.swing.GroupLayout.DEFAULT_SIZE, Short.MAX_VALUE))
        );

        javax.swing.GroupLayout panCalendarLayout = new javax.swing.GroupLayout(panCalendar);
        panCalendar.setLayout(panCalendarLayout);
        panCalendarLayout.setHorizontalGroup(
            panCalendarLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
            .addGap(0, 241, Short.MAX_VALUE)
        );
        panCalendarLayout.setVerticalGroup(
            panCalendarLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
            .addGap(0, 165, Short.MAX_VALUE)
        );

        javax.swing.GroupLayout layout = new javax.swing.GroupLayout(this);
        this.setLayout(layout);
        layout.setHorizontalGroup(
            layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
            .addComponent(panToolbar, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, Short.MAX_VALUE)
            .addComponent(panCalendar, javax.swing.GroupLayout.Alignment.TRAILING, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, Short.MAX_VALUE)
        );
        layout.setVerticalGroup(
            layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
            .addGroup(layout.createSequentialGroup()
                .addComponent(panToolbar, javax.swing.GroupLayout.PREFERRED_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.PREFERRED_SIZE)
                .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.RELATED)
                .addComponent(panCalendar, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, Short.MAX_VALUE))
        );
    }// </editor-fold>//GEN-END:initComponents

    private void btnPrevYearActionPerformed(java.awt.event.ActionEvent evt) {//GEN-FIRST:event_btnPrevYearActionPerformed
        // TODO add your handling code here:
    }//GEN-LAST:event_btnPrevYearActionPerformed

    // Variables declaration - do not modify//GEN-BEGIN:variables
    private javax.swing.JButton btnClear;
    private javax.swing.JButton btnNextMonth;
    private javax.swing.JButton btnNextYear;
    private javax.swing.JButton btnPrevMonth;
    private javax.swing.JButton btnPrevYear;
    private javax.swing.JLabel lbYear;
    private javax.swing.JPanel panCalendar;
    private javax.swing.JPanel panToolbar;
    // End of variables declaration//GEN-END:variables
}