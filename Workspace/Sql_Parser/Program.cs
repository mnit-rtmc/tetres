using System;
using System.IO;

namespace parsesqlfile
{
    internal class Program
    {
        public static void Main(string[] args)
        {
            // var pp = Path.GetDirectoryName(Assembly.GetExecutingAssembly().Location);
            // Console.WriteLine(pp);
            const string cadSrcFile = "..\\..\\mndot\\mndotcad.sql";
            const string cadDestFile = "..\\..\\out\\cadDataOnly.sql";
            ParseAndWriteCadDataOnly(cadSrcFile, cadDestFile);
            // CountCadLines(cadSrcFile);

            const string cadPrefixFile = "..\\..\\workspace\\cadPrefix.sql";
            const string cadDataOnlyFile = "..\\..\\out\\cadDataOnly.sql";
            const string cadPostfixFile = "..\\..\\workspace\\cadPostfix.sql";
            CombineCad(cadPrefixFile, cadDataOnlyFile, cadPostfixFile);

            const string topFile = "..\\..\\iris\\ins2018.sql";
            const string endFile = "..\\..\\iris\\ins2019.sql";
            const string outFile = "..\\..\\iris\\irisUpdate.sql";

            // CombineIris(topFile, endFile, outFile);
        }

        private static void CombineIris(string topFile, string endFile, string outFile)
        {
            Console.WriteLine($"Combining\n{topFile}\n{endFile}");
            StreamReader reader = null;
            StreamWriter writer = null;
            try
            {
                reader = new StreamReader(topFile);
                writer = new StreamWriter(outFile, append: true);

                while (!reader.EndOfStream)
                {
                    var line = reader.ReadLine();
                    writer.WriteLine(line);
                }

                reader.Close();
                reader.Dispose();
                reader = null;
                reader = new StreamReader(endFile);

                while (!reader.EndOfStream)
                {
                    var line = reader.ReadLine();
                    writer.WriteLine(line);
                }

                reader.Close();
                writer.Close();
                Console.WriteLine("Done");
            }
            catch (Exception ex)
            {
                Console.WriteLine(ex);
            }
            finally
            {
                reader?.Close();
                writer?.Close();
            }
        }

        private static void CombineCad(string srcTop, string srcMid, string srcEnd)
        {
            Console.WriteLine($"Combining {srcTop}\n{srcMid}\n{srcEnd}");
            StreamReader reader = null;
            StreamWriter writer = null;
            try
            {
                reader = new StreamReader(srcMid);
                writer = new StreamWriter(srcTop, append: true);

                while (!reader.EndOfStream)
                {
                    var line = reader.ReadLine();
                    writer.WriteLine(line);
                }

                reader.Close();
                reader.Dispose();
                reader = null;

                reader = new StreamReader(srcEnd);
                while (!reader.EndOfStream)
                {
                    var line = reader.ReadLine();
                    writer.WriteLine(line);
                }

                reader.Close();
                writer.Close();
                Console.WriteLine("Done");
            }
            catch (Exception ex)
            {
                Console.WriteLine(ex);
            }
            finally
            {
                reader?.Close();
                writer?.Close();
            }
        }

        private static void ParseTestingCad(string srcFile, string destFile)
        {
            Console.WriteLine($"Parsing {srcFile}\nto\n{destFile}");
            StreamReader reader = null;
            StreamWriter writer = null;
            try
            {
                reader = new StreamReader(srcFile);
                writer = new StreamWriter(destFile, append: true);

                long counter = 0;

                while (!reader.EndOfStream && counter < 1747)
                {
                    reader.ReadLine();
                    counter++;
                }

                while (!reader.EndOfStream && counter < 1775)
                {
                    var line = reader.ReadLine();
                    writer.WriteLine(line);
                    counter++;
                }


                reader.Close();
                writer.Close();
                Console.WriteLine("Done");
                Console.WriteLine($"Lines: {counter}");
            }
            catch (Exception ex)
            {
                Console.WriteLine(ex);
            }
            finally
            {
                reader?.Close();
                writer?.Close();
            }
        }

        private static void CountCadLines(string srcFile)
        {
            Console.WriteLine($"Counting {srcFile}");
            StreamReader reader = null;
            try
            {
                reader = new StreamReader(srcFile);

                long counter = 0;

                while (!reader.EndOfStream)
                {
                    reader.ReadLine();
                    counter++;
                }

                reader.Close();
                Console.WriteLine("Done");
                Console.WriteLine($"Lines: {counter}");
            }
            catch (Exception ex)
            {
                Console.WriteLine(ex);
            }
            finally
            {
                reader?.Close();
            }
        }

        private static void ParseAndWriteCadDataOnly(string srcFile, string destFile)
        {
            Console.WriteLine($"Parsing {srcFile}\nto\n{destFile}");
            StreamReader reader = null;
            StreamWriter writer = null;
            try
            {
                reader = new StreamReader(srcFile);
                writer = new StreamWriter(destFile, append: true);

                long counter = 0;

                while (!reader.EndOfStream && counter < 1747)
                {
                    reader.ReadLine();
                    counter++;
                }

                while (!reader.EndOfStream && counter < 34076238)
                {
                    var line = reader.ReadLine();
                    writer.WriteLine(line);
                    counter++;
                }


                reader.Close();
                writer.Close();
                Console.WriteLine("Done");
                Console.WriteLine($"Lines: {counter}");
            }
            catch (Exception ex)
            {
                Console.WriteLine(ex);
            }
            finally
            {
                reader?.Close();
                writer?.Close();
            }
        }
    }
}