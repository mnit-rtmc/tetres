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
package ticas.common.util;

import java.awt.Desktop;
import java.io.BufferedInputStream;
import java.io.BufferedOutputStream;
import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.File;
import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.io.FileReader;
import java.io.FileWriter;
import java.io.IOException;
import java.io.RandomAccessFile;
import java.nio.file.Files;
import java.util.ArrayList;
import java.util.Calendar;
import java.util.GregorianCalendar;
import java.util.List;
import java.util.StringTokenizer;
import java.util.logging.Level;
import java.util.logging.Logger;
import java.util.regex.Matcher;
import java.util.regex.Pattern;
import javax.swing.JFileChooser;
import javax.swing.JOptionPane;
import javax.swing.filechooser.FileFilter;
import javax.swing.filechooser.FileNameExtensionFilter;

/**
 *
 * @author Chongmyung Park
 */
public class FileHelper {

    public final static FileFilter FileFilterForAll = new FileFilter() {
        @Override
        public boolean accept(File f) {
            return true;
        }

        @Override
        public String getDescription() {
            return "All Files (*.*)";
        }
    };
    
    
    private static final char[] ILLEGAL_CHARACTERS = { '/', '\n', '\r', '\t', '\0', '\f', '`', '?', '*', '\\', '<', '>', '|', '\"', ':' };
    
    public final static FileNameExtensionFilter FileFilterForVISSIM = new FileNameExtensionFilter("VISSIM Case File (*.inp)", "inp");
    public final static FileNameExtensionFilter FileFilterForExcel = new FileNameExtensionFilter("Excel File (*.xlsx)", "xlsx");
    public final static FileNameExtensionFilter FileFilterForText = new FileNameExtensionFilter("Text File (*.txt)", "txt");
    public final static FileNameExtensionFilter FileFilterForConfig = new FileNameExtensionFilter("Configuration File (*.config)", "config");
    public final static FileNameExtensionFilter FileFilterForProperties = new FileNameExtensionFilter("Property File (*.properties)", "properties");
    public final static FileNameExtensionFilter FileFilterForXML = new FileNameExtensionFilter("XML File (*.xml)", "xml");
    public final static FileNameExtensionFilter FileFilterForCSV = new FileNameExtensionFilter("CSV File (*.csv)", "csv");
    public final static FileNameExtensionFilter FileFilterForVISSIMDATA = new FileNameExtensionFilter("VISSIM Result File (*.rsz,*.vlz)", "rsz", "vlz");

    public static String currentPath() {
        return System.getProperty("user.dir");
    }

    public static String chooseFileToSave() {
        return chooseFileToSave(".", "Save as...");
    }

    public static String chooseFileToSave(FileFilter filter) {
        return chooseFileToSave(".", "Save as...", filter);
    }

    public static String chooseFileToSave(String currentPath, String dialogTitle) {
        return chooseFileOrDirectory(currentPath, dialogTitle, JFileChooser.FILES_ONLY, null, 0);
    }

    public static String chooseFileToSave(String currentPath, String dialogTitle, FileFilter filter) {
        return chooseFileOrDirectory(currentPath, dialogTitle, JFileChooser.FILES_ONLY, new FileFilter[]{filter}, 0);
    }

    public static String chooseFileToOpen() {
        return chooseFileToOpen(".", "Open File");
    }

    public static String chooseFileToOpen(String currentPath, String dialogTitle) {
        return chooseFileToOpen(currentPath, dialogTitle, (FileFilter) null);
    }

    public static String chooseFileToOpen(String currentPath, String dialogTitle, FileFilter filter) {
        return chooseFileOrDirectory(currentPath, dialogTitle, JFileChooser.FILES_ONLY, new FileFilter[]{filter}, 1);
    }

    public static String chooseFileToOpen(String currentPath, String dialogTitle, FileFilter[] filters) {
        return chooseFileOrDirectory(currentPath, dialogTitle, JFileChooser.FILES_ONLY, filters, 1);
    }

    public static String[] chooseFiles() {
        return chooseFiles(".", "Open Files");
    }

    public static String[] chooseFiles(String currentPath, String dialogTitle) {
        return chooseFiles(currentPath, dialogTitle, (FileFilter) null);
    }

    public static String[] chooseFiles(String currentPath, String dialogTitle, FileFilter filter) {
        return chooseFileOrDirectorys(currentPath, dialogTitle, JFileChooser.FILES_ONLY, new FileFilter[]{filter});
    }

    public static String[] chooseFiles(String currentPath, String dialogTitle, FileFilter[] filters) {
        return chooseFileOrDirectorys(currentPath, dialogTitle, JFileChooser.FILES_ONLY, null);
    }

    public static String chooseDirectory() {
        return chooseDirectory(".", "Open Directory");
    }

    public static String chooseDirectory(String currentPath, String dialogTitle) {
        return chooseFileOrDirectory(currentPath, dialogTitle, JFileChooser.DIRECTORIES_ONLY, null, 1);
    }

    private static String chooseFileOrDirectory(String currentPath, String dialogTitle, int mode, FileFilter[] filters, int dialogType) {
        JFileChooser chooser = new JFileChooser();
        if (filters != null) {
            for (FileFilter f : filters) {
                chooser.addChoosableFileFilter(f);
            }
            chooser.addChoosableFileFilter(FileFilterForAll);
        }
        chooser.setCurrentDirectory(new java.io.File(currentPath));
        chooser.setDialogTitle(dialogTitle);
        chooser.setFileSelectionMode(mode);
        chooser.setAcceptAllFileFilterUsed(false);
        if (filters != null && filters.length > 0) {
            chooser.setFileFilter(filters[0]);
        }
        // open dialog
        if (dialogType == 1) {
            if (chooser.showOpenDialog(null) == JFileChooser.APPROVE_OPTION) {
                return chooser.getSelectedFile().getAbsolutePath();
            }
        } else // save dialog
         if (chooser.showSaveDialog(null) == JFileChooser.APPROVE_OPTION) {
                String sltPath = chooser.getSelectedFile().getAbsolutePath();
                if (dialogType == 0) {
                    FileFilter filter = chooser.getFileFilter();
                    if (filter instanceof FileNameExtensionFilter) {
                        FileNameExtensionFilter efilter = (FileNameExtensionFilter) filter;
                        boolean hasExt = false;
                        for (String ext : efilter.getExtensions()) {
                            if (sltPath.endsWith("." + ext)) {
                                hasExt = true;
                                break;
                            }
                        }
                        if (!hasExt) {
                            sltPath = sltPath + "." + efilter.getExtensions()[0];
                        }
                    }
                }
                return sltPath;
            }
        return null;
    }

    private static String[] chooseFileOrDirectorys(String currentPath, String dialogTitle, int mode, FileFilter[] filters) {
        JFileChooser chooser = new JFileChooser();
        if (filters != null) {
            for (FileFilter f : filters) {
                chooser.addChoosableFileFilter(f);
            }
        }
        chooser.setCurrentDirectory(new java.io.File(currentPath));
        chooser.setDialogTitle(dialogTitle);
        chooser.setFileSelectionMode(mode);
        chooser.setMultiSelectionEnabled(true);
        chooser.setAcceptAllFileFilterUsed(false);
        if (chooser.showOpenDialog(null) == JFileChooser.APPROVE_OPTION) {
            File[] files = chooser.getSelectedFiles();
            String[] filenames = new String[files.length];
            for (int i = 0; i < files.length; i++) {
                filenames[i] = files[i].getAbsolutePath();
            }
            return filenames;
        }
        return null;
    }

    /**
     * Method writeFile.
     *
     * @param contents
     * @param fullPathFilename
     * @throws IOException
     */
    public static void writeTextFile(String contents, String fullPathFilename) throws IOException {
        BufferedWriter writer = new BufferedWriter(new FileWriter(fullPathFilename));
        writer.write(contents);
        writer.flush();
        writer.close();
    }

    /**
     * Method readTextFile. Uses a FileReader to populate a buffer of chars. The
     * chars are appended to a StringBuffer and returned as a String to the
     * caller. The FileReader uses the default file encoding scheme for the OS.
     *
     * @param fullPathFilename
     * @return String
     * @throws IOException
     */
    public static String readTextFile(String fullPathFilename) throws IOException {
        StringBuilder sb = new StringBuilder(1024);
        BufferedReader reader = new BufferedReader(new FileReader(fullPathFilename));

        char[] chars = new char[1024];
        int numRead = 0;
        while ((numRead = reader.read(chars)) > -1) {
            sb.append(String.valueOf(chars, 0, numRead));
        }

        reader.close();

        return sb.toString();
    }

    public static ArrayList<String> readTextFileLines(String fullPathFilename) throws IOException {
        ArrayList<String> datas = new ArrayList();
        StringBuilder sb = new StringBuilder(1024);
        BufferedReader reader = new BufferedReader(new FileReader(fullPathFilename));

        char[] chars = new char[1024];
        String s;
        while ((s = reader.readLine()) != null) {
            datas.add(s);
        }

        reader.close();

        return datas;
    }

    public static void writeBinaryFile(byte[] contents, String fullPathFilename) throws IOException {
        BufferedOutputStream bos = new BufferedOutputStream(new FileOutputStream(fullPathFilename));
        bos.write(contents);
        bos.flush();
        bos.close();

    }

    public static String tail(String fullPathFilename, int charsToRead, String charSet) throws IOException {
        if (charSet == null) {
            charSet = "latin1";
        }
        RandomAccessFile raf = new RandomAccessFile(fullPathFilename, "r");
        long posToStart = raf.length() - charsToRead;
        byte[] bytes = new byte[charsToRead];

        raf.seek(posToStart);
        raf.readFully(bytes);
        raf.close();
        return new String(bytes, charSet);
    }

//    /**
//     * Method countWords. This supposes that a word is a space-delimited String.
//     * This would be trivial but for the possibility of multiple spaces between
//     * words.
//     *
//     * @param fullPathFilename
//     * @return int
//     */
//    public static int countWords(String fullPathFilename) throws IOException {
//
//        BufferedReader reader = new BufferedReader(new FileReader(fullPathFilename));
//
//        String line;
//        char[] chars;
//        int wordCount = 0;
//
//        while ((line = reader.readLine()) != null) {
//
//            chars = line.toCharArray();
//            wordCount++;
//
//            for (int i = 1; i < chars.length - 1; i++) {
//                if (Character.isSpace(chars[i]) && Character.isJavaLetterOrDigit(chars[i + 1])) {
//                    wordCount++;
//
//                }
//            }
//
//        }
//
//        reader.close();
//
//        return wordCount;
//    }
    public static String[][] readCSV(String fullPathFilename, int numToRead) throws IOException {
        BufferedReader reader = new BufferedReader(new FileReader(fullPathFilename));
        String line;
        StringTokenizer st;
        int size = 0;
        int index = 0;
        int pos = 1; //skip the first position.
        String[][] data;
        String[][] temp;
        final int DEFAULT_SIZE = 250;
        final String DELIMITER = ",";
        int maxRecords;

        //read the first line to get the size of the array
        line = reader.readLine();
        st = new StringTokenizer(line, DELIMITER);
        while (st.hasMoreElements()) {
            st.nextElement();
            size++;
        }

        //size the array, if parameter not set, read the entire file
        //otherwise stop as requested.
        if (numToRead == 0) {
            numToRead = DEFAULT_SIZE;
            maxRecords = Integer.MAX_VALUE;
        } else {
            maxRecords = numToRead;
        }

        data = new String[numToRead][size];

        //do it again to add to the array
        st = new StringTokenizer(line, DELIMITER);
        while (st.hasMoreElements()) {
            data[0][index] = st.nextElement().toString();
            index++;
        }
        index = 0;

        //now do a bunch..
        while ((line = reader.readLine()) != null && pos < maxRecords) {
            st = new StringTokenizer(line, DELIMITER);
            while (st.hasMoreElements()) {
                if (index == data[0].length) {
                    break;
                }
                data[pos][index] = st.nextElement().toString();
                index++;
            }
            index = 0;
            pos++;

            if (pos == data.length - 1) { //size array if needed.
                temp = new String[data.length + numToRead][size];
                for (int n = 0; n < data.length; n++) {
                    System.arraycopy(data[n], 0, temp[n], 0, temp[n].length);
                }
                data = temp;

            }

        }

        //size the array correctly.. it may be too large.
        temp = new String[pos][size];// the size read
        for (int n = 0; n < temp.length; n++) {
            System.arraycopy(data[n], 0, temp[n], 0, temp[n].length);
        }

        reader.close();
        return temp;

    }

    public static void copy(File source, File destination) throws IOException {

        BufferedInputStream bis = new BufferedInputStream(new FileInputStream(source));
        BufferedOutputStream bos = new BufferedOutputStream(new FileOutputStream(destination));
        int numRead;
        byte[] bytes = new byte[1024];
        while ((numRead = bis.read(bytes)) != -1) {
            bos.write(bytes, 0, numRead);
        }

        try {
            bis.close();
        } catch (Exception e) {
        }

        try {
            bos.close();
        } catch (Exception e) {
        }
    }

    public static void appendToTextFile(String contents, String fullPathFilename) throws IOException {
        BufferedWriter writer = new BufferedWriter(new FileWriter(fullPathFilename, true));
        writer.write(contents);
        writer.flush();
        writer.close();
    }

    /**
     * Get file name to save in order to overwrite
     *
     * @param filePath option name for txt file (txt file should be made
     * multiple file)
     * @return filepath string
     */
    public static String getNumberedFileName(String filePath) {

        Filename filename = new Filename(filePath, File.separatorChar, '.');
        String ext = filename.extension();
        String name = filename.filename();
        String path = filename.path();

        String filepath = filePath;

        int count = 0;
        while (true) {
            File file = new File(filepath);
            if (!file.exists()) {
                break;
            }
            filepath = path + File.separator + name + " (" + (++count) + ")" + "." + ext;
        }

        return filepath;
    }

    public static String getExtension(String filePath) {
        return new Filename(filePath, File.separatorChar, '.').extension();
    }

    public static String getFileNameWithoutExtension(String filePath) {
        return new Filename(filePath, File.separatorChar, '.').filename();
    }

    public static String checkExtension(String path, FileNameExtensionFilter filter) {
        String ext = getExtension(path);
        for (String extension : filter.getExtensions()) {
            if (extension.equals(ext)) {
                return path;
            }
        }
        return path + "." + filter.getExtensions()[0];
    }

    public static boolean exists(String filePath) {
        return new File(filePath).exists();
    }

    public static boolean createDirs(String dirPath) {
        return new File(dirPath).mkdirs();
    }

    public static String absolutePath(String relPath) {
        try {
            return new File(relPath).getCanonicalPath();
        } catch (IOException ex) {
            return "";
        }
    }

    public static void openDirectory(String dirPath) {
        Desktop desktop = Desktop.getDesktop();
        File dirToOpen = null;
        try {
            dirToOpen = new File(dirPath);
            desktop.open(dirToOpen);
        } catch (IllegalArgumentException iae) {
            JOptionPane.showMessageDialog(null, "Folder Not Found");
        } catch (IOException ex) {
            JOptionPane.showMessageDialog(null, "Exception occured to open folder");
        }
    }

    public static boolean isFilenameValid(String filename) {
        if(filename == null || filename.isEmpty()) {
            return false;
        }
        for(char ch : ILLEGAL_CHARACTERS) {
            if(filename.indexOf(ch) >= 0) {
                return false;
            }
        }
        return true;
    }    

    public static List<String> listFiles(String dirPath, boolean getName) {
        File folder = new File(dirPath);
        List<String> files = new ArrayList<String>();
        File[] listOfFiles = folder.listFiles();
        for (int i = 0; i < listOfFiles.length; i++) {
            if (listOfFiles[i].isFile()) {
                if (getName) {
                    files.add(listOfFiles[i].getName());
                } else {
                    files.add(listOfFiles[i].getAbsolutePath());
                }
            }
        }
        return files;
    }

    public static List<String> listDirectories(String dirPath, boolean getName) {
        File folder = new File(dirPath);
        List<String> dirs = new ArrayList<String>();
        File[] listOfFiles = folder.listFiles();
        for (int i = 0; i < listOfFiles.length; i++) {
            if (listOfFiles[i].isDirectory()) {
                if (getName) {
                    dirs.add(listOfFiles[i].getName());
                } else {
                    dirs.add(listOfFiles[i].getAbsolutePath());
                }
            }
        }
        return dirs;
    }

    static class Filename {

        private String fullPath;
        private char pathSeparator, extensionSeparator;

        public Filename(String str, char sep, char ext) {
            fullPath = new File(str).getAbsolutePath();
            pathSeparator = sep;
            extensionSeparator = ext;
        }

        public String extension() {
            try {
                int dot = fullPath.lastIndexOf(extensionSeparator);
                return fullPath.substring(dot + 1);
            } catch (Exception ex) {
                return "";
            }
        }

        public String filename() { // gets filename without extension            
            int dot = fullPath.lastIndexOf(extensionSeparator);
            int sep = fullPath.lastIndexOf(pathSeparator);
            if (dot < 0) {
                dot = fullPath.length() - 1;
            }
            if (sep < 0) {
                sep = 0;
            }
            return fullPath.substring(sep + 1, dot);
        }

        public String path() {
            int sep = fullPath.lastIndexOf(pathSeparator);
            if (sep < 0) {
                return "";
            }
            return fullPath.substring(0, sep);
        }
    }

    public static void deleteDirectory(String filepath) {
        File f = new File(filepath);
        if (f.isDirectory()) {
            for (File c : f.listFiles()) {
                deleteDirectory(c.getAbsolutePath());
            }
        }
        f.delete();
    }

    public static void deleteOldFiles(int hours, String filepath) {
        File f = new File(filepath);
        if (f.isDirectory()) {
            for (File c : f.listFiles()) {
                deleteOldFiles(hours, c.getAbsolutePath());
            }
        }
        Calendar cal = Calendar.getInstance();
        cal.add(Calendar.HOUR, hours * -1);
        long purgeTime = cal.getTimeInMillis();
        Calendar cal2 = GregorianCalendar.getInstance();
        cal2.setTimeInMillis(f.lastModified());
        if (f.lastModified() < purgeTime) {
            try {
                Files.delete(f.toPath());
            } catch (IOException ex) {
                System.err.println("Unable to delete file : " + f.getPath());
            }
        }
    }
}
