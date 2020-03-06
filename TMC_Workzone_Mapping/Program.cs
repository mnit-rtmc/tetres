using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text.RegularExpressions;
using System.Xml;
using System.Xml.Linq;

namespace TMC_Workzone_Mapping
{
    class Program
    {
        private const string TmcDataPath = "./assets/TMC_Data";
        private const string StationDataPath = "./assets/Station_Data";
        private const string GenDataPath = "./assets/Generated_Output_Files";

        private static readonly List<TmcGroup> TmcGroups = new List<TmcGroup>();
        private static readonly List<TmcReadings> TmcReadingsList = new List<TmcReadings>();
        private static readonly List<Station> StationList = new List<Station>();

        private static void Main(string[] args)
        {
            ParseTmcIds($"{TmcDataPath}/tmc_ids_all_corridors_94694_renamed_94.csv");
            ParseTmcReadings($"{TmcDataPath}/tmc_readings_all_corridors.csv");
            PairTmcIdsWithReadings();

            ParseMetroXml($"{StationDataPath}/MetroXML-2020-01-22.xml",
                $"{GenDataPath}/GeneratedXmlStationOutput.xml");

            ParseGeneratedXmlStationOutput($"{GenDataPath}/GeneratedXmlStationOutput.xml");


            MatchStationsToTmcs();
            // TmcGroups.ForEach(g => Console.WriteLine(
            //     $"TmcGroup Corridor[{g.Corridor}] Keys Count[{g.TsMap.Keys.Count}]"));


            WriteTmcStationMatchesFile($"{GenDataPath}/TmcStationMatches.xml");

            var kmlBuilder = new KmlBuilder(TmcGroups, StationList);
            kmlBuilder.Run($"{GenDataPath}/");


            Console.WriteLine("Finished");
        }

        private static void WriteTmcStationMatchesFile(string filePath)
        {
            try
            {
                XDocument document = new XDocument();
                XElement root = new XElement("tmc_station_matches");

                TmcGroups.ForEach(g =>
                {
                    var xeGroup = new XElement("tmc_group");
                    xeGroup.SetAttributeValue("corridor", g.Corridor);
                    xeGroup.SetAttributeValue("direction", g.Direction);
                    xeGroup.SetAttributeValue("tmc_count", g.TmcList.Count);

                    foreach (var keyValuePair in g.TsMap)
                    {
                        var xeTmc = new XElement("tmc");
                        xeTmc.SetAttributeValue("id", keyValuePair.Key.TmcId);
                        xeTmc.SetAttributeValue("corridor", keyValuePair.Key.Corridor);
                        xeTmc.SetAttributeValue("start_lat", keyValuePair.Key.StartLat);
                        xeTmc.SetAttributeValue("start_lon", keyValuePair.Key.StartLon);
                        xeTmc.SetAttributeValue("end_lat", keyValuePair.Key.EndLat);
                        xeTmc.SetAttributeValue("end_lon", keyValuePair.Key.EndLon);

                        keyValuePair.Value.ForEach(s =>
                        {
                            var xeS = new XElement("station");
                            xeS.SetAttributeValue("id", s.Id);
                            xeS.SetAttributeValue("corridor", s.Corridor);
                            xeS.SetAttributeValue("lat", s.Lat);
                            xeS.SetAttributeValue("lon", s.Lon);
                            xeTmc.Add(xeS);
                        });
                        xeGroup.Add(xeTmc);
                    }

                    root.Add(xeGroup);
                });
                document.Add(root);

                XmlWriterSettings xws = new XmlWriterSettings();
                xws.OmitXmlDeclaration = false;
                xws.Indent = true;

                using (XmlWriter xw = XmlWriter.Create(filePath, xws))
                {
                    document.Save(xw);
                }
            }
            catch (Exception e)
            {
                Console.ForegroundColor = ConsoleColor.Red;
                Console.WriteLine(e);
                Console.ResetColor();
            }
        }

        private static void MatchStationsToTmcs()
        {
            Console.ForegroundColor = ConsoleColor.Green;
            Console.WriteLine("Matching Stations To TMC's...");
            Console.ResetColor();

            try
            {
                TmcGroups.ForEach(g =>
                {
                    // Console.ForegroundColor = ConsoleColor.Cyan;
                    // Console.WriteLine($"{g.Corridor} {g.Direction}");
                    // Console.ForegroundColor = ConsoleColor.Magenta;
                    // StationList.ForEach(s => Console.Write($"{s.Corridor} {s.Direction}"));
                    // Console.ResetColor();

                    var sInRoute = StationList.TakeWhile(sr =>
                        sr.Corridor == g.Corridor && sr.Direction == g.Direction).ToList();


                    g.TmcList.ForEach(tmc =>
                    {
                        var sInTmc = sInRoute.TakeWhile(sr =>
                            sr.Lat <= Math.Max(tmc.StartLat, tmc.EndLat) &&
                            sr.Lat >= Math.Min(tmc.StartLat, tmc.EndLat) &&
                            sr.Lon <= Math.Max(tmc.StartLon, tmc.EndLon) &&
                            sr.Lon >= Math.Min(tmc.StartLon, tmc.EndLon)
                        ).ToList();
                        if (sInTmc.Count > 0)
                        {
                            g.TsMap.Add(tmc, sInTmc);
                        }
                    });
                });
            }
            catch (Exception e)
            {
                Console.ForegroundColor = ConsoleColor.Red;
                Console.WriteLine(e);
                Console.ResetColor();
            }
        }

        private static void ParseMetroXml(string metroXmlPath, string writePath)
        {
            Console.ForegroundColor = ConsoleColor.Green;
            Console.WriteLine("Parsing Metro Xml File...");
            Console.ResetColor();

            Regex regexNumeric = new Regex(@"[^\d]");

            try
            {
                var metroxml = XElement.Load(metroXmlPath);

                XDocument document = new XDocument();
                XElement root = new XElement("parsed-metro-xml");
                IEnumerable<XElement> corr = metroxml.Descendants("corridor").Select(x => x).ToList();

                var corrList = corr.ToList();
                corrList.ForEach(c =>
                {
                    var xElement = new XElement("corridor");
                    xElement.SetAttributeValue("route",
                        //TODO:
                        // regexNumeric.Replace((string) c.Attribute("route"), "")
                        ((string) c.Attribute("route")).Replace(" ", "")
                        // c.Attribute("route")
                    );
                    xElement.SetAttributeValue("dir",
                        ((string) c.Attribute("dir")).Replace(" ", ""));

                    var stationsList = c.Descendants("r_node").Where(
                        e => e.Attributes("station_id").Any()).Select(xe => xe).ToList();

                    stationsList.ForEach(s =>
                    {
                        var xElementStation = new XElement("station");
                        xElementStation.SetAttributeValue("station_id",
                            ((string) s.Attribute("station_id")).Replace(" ", ""));
                        xElementStation.SetAttributeValue("lon", (string) s.Attribute("lon"));
                        xElementStation.SetAttributeValue("lat", (string) s.Attribute("lat"));
                        xElement.Add(xElementStation);
                    });

                    if (xElement.Descendants("station").Any())
                    {
                        root.Add(xElement);
                    }
                });
                document.Add(root);

                XmlWriterSettings xws = new XmlWriterSettings();
                xws.OmitXmlDeclaration = false;
                xws.Indent = true;

                using (XmlWriter xw = XmlWriter.Create(writePath, xws))
                {
                    document.Save(xw);
                }
            }
            catch (Exception e)
            {
                Console.ForegroundColor = ConsoleColor.Red;
                Console.WriteLine(e);
                Console.ResetColor();
            }
        }

        private static void ParseGeneratedXmlStationOutput(string stationXmlPath)
        {
            Console.ForegroundColor = ConsoleColor.Green;
            Console.WriteLine("Parsing Generated Stations List XML File...");
            Console.ResetColor();

            try
            {
                var stationXml = XElement.Load(stationXmlPath);

                List<XElement> corrList = stationXml.Descendants("corridor").Select(x => x).ToList();

                corrList.ForEach(c =>
                {
                    var corridor = c.Attribute("route")?.Value;
                    var direction = c.Attribute("dir")?.Value;
                    var stationsList = c.Descendants("station").Select(xe => xe).ToList();
                    Console.ForegroundColor = ConsoleColor.Cyan;
                    Console.WriteLine($"{corridor} {direction}");
                    stationsList.ForEach(s =>
                    {
                        var stationId = s.Attribute("station_id")?.Value;
                        var lat = s.Attribute("lat")?.Value;
                        var lon = s.Attribute("lon")?.Value;

                        StationList.Add(new Station
                        {
                            Corridor = corridor,
                            Direction = direction,
                            Id = stationId,
                            Lat = double.TryParse(lat, out var sLat) ? sLat : double.NaN,
                            Lon = double.TryParse(lon, out var sLong) ? sLong : double.NaN
                        });
                    });
                });
                Console.ResetColor();
            }
            catch (Exception e)
            {
                Console.ForegroundColor = ConsoleColor.Red;
                Console.WriteLine(e);
                Console.ResetColor();
            }
        }

        private static void PairTmcIdsWithReadings()
        {
            Console.ForegroundColor = ConsoleColor.Green;
            Console.WriteLine("Paring Tmc's With Tmc Readings...");
            Console.ResetColor();

            foreach (var tmcGroup in TmcGroups)
            {
                foreach (var tmc in tmcGroup.TmcList)
                {
                    try
                    {
                        tmc.TmcReads = TmcReadingsList.Find(tr => tr.TmcId == tmc.TmcId);
                    }
                    catch (Exception e)
                    {
                        Console.ForegroundColor = ConsoleColor.Red;
                        Console.WriteLine(e);
                        Console.ResetColor();
                    }
                }
            }
        }

        private static void ParseTmcReadings(string filePath)
        {
            Console.ForegroundColor = ConsoleColor.Green;
            Console.WriteLine("Parsing Tmc Readings File...");
            Console.ResetColor();

            char[] delimC = {','};

            StreamReader reader = null;
            try
            {
                reader = new StreamReader(filePath);
                if (!reader.EndOfStream) reader.ReadLine();

                string[] line = null;
                do
                {
                    line = SubParseTmcReadings(line, reader);
                } while (line != null);


                string[] SubParseTmcReadings(string[] pLine, StreamReader pReader)
                {
                    if (pReader.EndOfStream) return null;
                    if (pLine == null) pLine = pReader.ReadLine()?.Split(delimC);

                    var tr = new TmcReadings {TmcId = pLine?[0]};
                    Assign(tr, pLine);

                    while (!pReader.EndOfStream)
                    {
                        pLine = pReader.ReadLine()?.Split(delimC);

                        if (!(pLine?[0]?.Equals(tr.TmcId) ?? false))
                        {
                            TmcReadingsList.Add(tr);
                            return pLine;
                        }

                        Assign(tr, pLine);
                    }

                    return null;

                    void Assign(TmcReadings t, string[] l)
                    {
                        t.TimeStamps.Add(l?[1]);
                        t.Speeds.Add(double.TryParse(l?[2], out var s) ? s : double.NaN);
                        t.AvgSpeeds.Add(double.TryParse(l?[3], out var avgS) ? avgS : double.NaN);
                        t.RefSpeeds.Add(double.TryParse(l?[4], out var rS) ? rS : double.NaN);
                        t.TravelTimes.Add(double.TryParse(l?[5], out var tT) ? tT : double.NaN);
                        t.DataDensities.Add(l?[6]);
                    }
                }
            }
            catch (Exception e)
            {
                Console.ForegroundColor = ConsoleColor.Red;
                Console.WriteLine(e);
                Console.ResetColor();
            }
            finally
            {
                reader?.Close();
            }
        }

        private static void ParseTmcIds(string filePath)
        {
            Console.ForegroundColor = ConsoleColor.Green;
            Console.WriteLine("Parsing Tmc List File...");
            Console.ResetColor();

            Console.ForegroundColor = ConsoleColor.Magenta;

            char[] delimC = {','};
            Regex regexNumeric = new Regex(@"[^\d]");
            StreamReader reader = null;
            try
            {
                reader = new StreamReader(filePath);
                if (!reader.EndOfStream) reader.ReadLine();

                while (!reader.EndOfStream)
                {
                    var line = reader.ReadLine()?.Split(delimC);

                    if (line != null && line.Length >= 11)
                    {
                        if (TmcGroups.Count == 0)
                        {
                            TmcGroups.Add(new TmcGroup(
                                //TODO:
                                // regexNumeric.Replace(line[1], ""),
                                line[1],
                                AbvDirectionString(line[2])
                            ));
                        }
                        else if (regexNumeric.Replace(line[1], "")
                                 != TmcGroups.Last().Corridor)
                        {
                            TmcGroups.Add(new TmcGroup(
                                //TODO:
                                // regexNumeric.Replace(line[1], ""),
                                line[1],
                                AbvDirectionString(line[2])
                            ));
                        }

                        TmcGroups.Last().TmcList.Add(new Tmc
                            {
                                TmcId = line[0],
                                Corridor = line[1],
                                //TODO:
                                // Corridor = regexNumeric.Replace(line[1], ""),

                                StartLat = double.TryParse(line[7], out var sLat) ? sLat : double.NaN,
                                StartLon = double.TryParse(line[8], out var sLon) ? sLon : double.NaN,
                                EndLat = double.TryParse(line[9], out var eLat) ? eLat : double.NaN,
                                EndLon = double.TryParse(line[10], out var eLon) ? eLon : double.NaN,
                            }
                        );
                    }
                }

                TmcGroups.ForEach(g => { Console.WriteLine($"{g.Corridor} {g.Direction}"); });

                reader.Close();
            }
            catch (Exception e)
            {
                Console.ForegroundColor = ConsoleColor.Red;
                Console.WriteLine(e);
                Console.ResetColor();
            }
            finally
            {
                reader?.Close();
            }

            string AbvDirectionString(string dir)
            {
                switch (dir)
                {
                    case "NORTHBOUND":
                        return "NB";
                    case "EASTBOUND":
                        return "EB";
                    case "SOUTHBOUND":
                        return "SB";
                    case "WESTBOUND":
                        return "WB";
                    default:
                        return "ERR";
                }
            }
        }

        List<string> corridorRegectList = new List<string>
        {
            "I-35ECD",
            "I-35WCD",
            "I-394CD",
            "I-394Rev",
            "T.H.53",
            "CR-53",
            "CR-63",
            ""
            
        };
        
        private static void CleanCorridorName(string corridor)
        {
            Regex regexNumeric = new Regex(@"[^\d]");
            var res = regexNumeric.Replace(corridor, "");
            
            res = res = corridor.Replace("T.H.", "MN-");
            res = res.Replace("I-394Rev", "I-394");
            res = res.Replace("U.S.", "US");

        }
    }
}