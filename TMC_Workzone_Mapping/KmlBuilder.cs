using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text;

namespace TMC_Workzone_Mapping
{
    public class KmlBuilder
    {
        private const string PointStyle = "<styleUrl>#icon-1899-000000-nodesc</styleUrl>";
        private const string LineStyle = "<styleUrl>#line-000000-1200</styleUrl>";

        private List<TmcGroup> _tmcGroupsList;
        private List<Station> _stationList;

        public KmlBuilder(List<TmcGroup> tmcGroupsList, List<Station> stationList)
        {
            _tmcGroupsList = tmcGroupsList;
            _stationList = stationList;
        }

        public void Run(string dirPath)
        {
            var datetime = (long) (DateTime.Now.ToUniversalTime()
                                   - new DateTime(1970, 1, 1, 0, 0, 0, DateTimeKind.Utc)
                ).TotalMilliseconds;

            string resPath = $"{dirPath}/{datetime}";
            Directory.CreateDirectory(resPath);


            // foreach (var tmcGroup in _tmcGroupsList)
            // {
            //     GenerateKmlFile($"{resPath}/tmc_group_{tmcGroup.CorridorRouteNumber}.kml", tmcGroup);
            // }

            IEnumerable<List<T>> splitList<T>(List<T> locations, int nSize = 3)
            {
                for (int i = 0; i < locations.Count; i += nSize)
                {
                    yield return locations.GetRange(i, Math.Min(nSize, locations.Count - i));
                }
            }

            var x = splitList(_tmcGroupsList, nSize: 5);

            Random random = new Random();

            foreach (var tmcGroupsList in x)
            {
                GenerateKmlFileAllLayers($"{resPath}/{random.Next(11111111, 99999999)}.kml", tmcGroupsList);
            }
        }

        private void GenerateKmlFileAllLayers(string filePath, List<TmcGroup> tmcGroupSubList)
        {
            StreamWriter writer = null;
            try
            {
                Console.ForegroundColor = ConsoleColor.Green;
                Console.WriteLine("Writing KML File...");
                Console.ResetColor();
                
                writer = new StreamWriter(filePath);

                AddDocument(writer, () =>
                {
                    foreach (var tmcGroup in tmcGroupSubList)
                    {
                        AddFolder(writer, $"{tmcGroup.Corridor}", () =>
                        {
                            foreach (var s in _stationList.Where(s => s.Corridor == tmcGroup.Corridor))
                            {
                                AddPlacemark(writer, s.Id, s.ToString(),
                                    PointStyle, () =>
                                    {
                                        AddPoint(writer, new List<MapItemCoordinates>
                                        {
                                            new MapItemCoordinates {X = s.Lon, Y = s.Lat, Z = 0}
                                        });
                                    });
                            }

                            foreach (var t in tmcGroup.TmcList)
                            {
                                AddPlacemark(writer, t.TmcId,
                                    t.StartLon + " " + t.StartLat + "\n" + t.EndLon + " " + t.EndLat,
                                    LineStyle, () =>
                                    {
                                        AddLineString(writer, new List<MapItemCoordinates>
                                        {
                                            new MapItemCoordinates {X = t.StartLon, Y = t.StartLat, Z = 0},
                                            new MapItemCoordinates {X = t.EndLon, Y = t.EndLat, Z = 0}
                                        });
                                    });
                            }
                        });
                    }
                });
                writer.Close();
            }
            catch (Exception e)
            {
                Console.ForegroundColor = ConsoleColor.Red;
                Console.WriteLine(e);
                Console.ResetColor();
            }
            finally
            {
                writer?.Close();
            }
        }

        private void GenerateKmlFile(string filePath, TmcGroup tmcGroup)
        {
            StreamWriter writer = null;
            try
            {
                Console.ForegroundColor = ConsoleColor.Green;
                Console.WriteLine("Writing KML File...");
                Console.ResetColor();
                
                writer = new StreamWriter(filePath);

                AddDocument(writer, () =>
                {
                    AddFolder(writer, $"{tmcGroup.Corridor}", () =>
                    {
                        foreach (var s in _stationList.Where(s => s.Corridor == tmcGroup.Corridor))
                        {
                            AddPlacemark(writer, s.Id, s.ToString(),
                                PointStyle, () =>
                                {
                                    AddPoint(writer, new List<MapItemCoordinates>
                                    {
                                        new MapItemCoordinates {X = s.Lon, Y = s.Lat, Z = 0}
                                    });
                                });
                        }

                        foreach (var t in tmcGroup.TmcList)
                        {
                            AddPlacemark(writer, t.TmcId,
                                t.StartLon + " " + t.StartLat + "\n" + t.EndLon + " " + t.EndLat,
                                LineStyle, () =>
                                {
                                    AddLineString(writer, new List<MapItemCoordinates>
                                    {
                                        new MapItemCoordinates {X = t.StartLon, Y = t.StartLat, Z = 0},
                                        new MapItemCoordinates {X = t.EndLon, Y = t.EndLat, Z = 0}
                                    });
                                });
                        }
                    });
                });
                writer.Close();
            }
            catch (Exception e)
            {
                Console.ForegroundColor = ConsoleColor.Red;
                Console.WriteLine(e);
                Console.ResetColor();
            }
            finally
            {
                writer?.Close();
            }
        }

        private void AddDocument(StreamWriter writer, Action action = null)
        {
            try
            {
                var s1 = new StringBuilder("<?xml version=\"1.0\" encoding=\"UTF-8\"?>" +
                                           "<kml xmlns=\"http://www.opengis.net/kml/2.2\">" +
                                           "<Document><name>Untitled map</name><description/>");

                writer.WriteLine(s1.ToString());
                AddStyles(writer);
                action?.Invoke();
                writer.WriteLine("</Document></kml>");
            }
            catch (Exception e)
            {
                Console.ForegroundColor = ConsoleColor.Red;
                Console.WriteLine(e);
                Console.ResetColor();
            }
        }

        private void AddStyles(StreamWriter writer)
        {
            try
            {
                var s1 = new StringBuilder(
                    "<Style id=\"icon-1899-000000-nodesc-normal\">" +
                    "<IconStyle><color>ff000000</color><scale>1</scale><Icon>" +
                    "<href>http://www.gstatic.com/mapspro/images/stock/503-wht-blank_maps.png</href>" +
                    "</Icon><hotSpot x=\"32\" xunits=\"pixels\" y=\"64\" yunits=\"insetPixels\"/>" +
                    "</IconStyle><LabelStyle><scale>0</scale></LabelStyle><BalloonStyle><text>" +
                    "<![CDATA[<h3>$[name]</h3>]]></text></BalloonStyle></Style>" +
                    "<Style id=\"icon-1899-000000-nodesc-normal\">" +
                    "<IconStyle><color>ff000000</color><scale>1</scale><Icon>" +
                    "<href>http://www.gstatic.com/mapspro/images/stock/503-wht-blank_maps.png</href>" +
                    "</Icon><hotSpot x=\"32\" xunits=\"pixels\" y=\"64\" yunits=\"insetPixels\"/>" +
                    "</IconStyle><LabelStyle><scale>1</scale></LabelStyle><BalloonStyle><text>" +
                    "<![CDATA[<h3>$[name]</h3>]]></text></BalloonStyle></Style>" +
                    "<StyleMap id=\"icon-1899-000000-nodesc\"><Pair><key>normal</key>" +
                    "<styleUrl>#icon-1899-000000-nodesc-normal</styleUrl></Pair><Pair><key>highlight</key>" +
                    "<styleUrl>#icon-1899-000000-nodesc-highlight</styleUrl></Pair></StyleMap>");


                var s2 = new StringBuilder(
                    "<Style id=\"line-000000-1200-normal\"><LineStyle><color>ff000000</color><width>3.325</width>" +
                    "</LineStyle></Style><Style id=\"line-000000-1200-highlight\"><LineStyle><color>ff000000</color>" +
                    "<width>4.9875</width></LineStyle></Style><StyleMap id=\"line-000000-1200\"><Pair><key>normal</key>" +
                    "<styleUrl>#line-000000-1200-normal</styleUrl></Pair><Pair><key>highlight</key>" +
                    "<styleUrl>#line-000000-1200-highlight</styleUrl></Pair></StyleMap>");


                writer.WriteLine(s1.ToString());
                writer.WriteLine(s2.ToString());
            }
            catch (Exception e)
            {
                Console.ForegroundColor = ConsoleColor.Red;
                Console.WriteLine(e);
                Console.ResetColor();
            }
        }

        private void AddFolder(StreamWriter writer, string name = "Folder", Action action = null)
        {
            // gets function of AddPlacemark calls passed
            try
            {
                writer.WriteLine("<Folder>");
                writer.WriteLine("<name>{0}</name>", name);
                action?.Invoke();
                writer.WriteLine("</Folder>");
            }
            catch (Exception e)
            {
                Console.ForegroundColor = ConsoleColor.Red;
                Console.WriteLine(e);
                Console.ResetColor();
            }
        }

        private void AddPlacemark(StreamWriter writer, string name,
            string description, string styleUrl, Action action = null)
        {
            // gets function of AddPoint or AddLineString calls passed
            try
            {
                writer.WriteLine("<Placemark>");
                writer.WriteLine("<name>{0}</name>", name);
                writer.WriteLine("<description>{0}</description>", description);
                writer.WriteLine(styleUrl);
                action?.Invoke();
                writer.WriteLine("</Placemark>");
            }
            catch (Exception e)
            {
                Console.ForegroundColor = ConsoleColor.Red;
                Console.WriteLine(e);
                Console.ResetColor();
            }
        }

        private void AddPoint(StreamWriter writer, List<MapItemCoordinates> coordinates)
        {
            try
            {
                writer.WriteLine("<Point>");
                writer.WriteLine("<coordinates>");
                coordinates.ForEach(e => writer.WriteLine("{0},{1},{2}", e.X, e.Y, e.Z));
                writer.WriteLine("</coordinates>");
                writer.WriteLine("</Point>");
            }
            catch (Exception e)
            {
                Console.ForegroundColor = ConsoleColor.Red;
                Console.WriteLine(e);
                Console.ResetColor();
            }
        }

        private void AddLineString(StreamWriter writer, List<MapItemCoordinates> coordinates)
        {
            try
            {
                writer.WriteLine("<LineString>");
                writer.WriteLine("<tessellate>1</tessellate>");
                writer.WriteLine("<coordinates>");
                coordinates.ForEach(e => writer.WriteLine("{0},{1},{2}", e.X, e.Y, e.Z));
                writer.WriteLine("</coordinates>");
                writer.WriteLine("</LineString>");
            }
            catch (Exception e)
            {
                Console.ForegroundColor = ConsoleColor.Red;
                Console.WriteLine(e);
                Console.ResetColor();
            }
        }
    }

    public class MapItemCoordinates
    {
        public double X { get; set; }
        public double Y { get; set; }
        public double Z { get; set; }
    }
}