using System.Collections.Generic;

namespace TMC_Workzone_Mapping
{
    public class TmcGroup
    {
        public string Corridor { get; set; }
        public string Direction { get; set; }
        public List<Tmc> TmcList;
        public Dictionary<Tmc, List<Station>> TsMap = new Dictionary<Tmc, List<Station>>();

        public TmcGroup(string corridor, string direction)
        {
            Corridor = corridor;
            Direction = direction;
            TmcList = new List<Tmc>();
        }
    }


    public class Tmc
    {
        public string TmcId { get; set; }
        public string Corridor { get; set; }
        public double StartLat { get; set; }
        public double EndLat { get; set; }
        public double StartLon { get; set; }
        public double EndLon { get; set; }
        public TmcReadings TmcReads { get; set; }


        public override string ToString()
        {
            return $"TmcId[{TmcId}]\nRoadName[{Corridor}]\n" +
                   $"StartLat[{StartLat}]\nStartLong[{StartLon}]\n" +
                   $"EndLat[{EndLat}]\nEndLong[{EndLon}]\n";
        }
    }

    public class TmcReadings
    {
        //Change DataDensities to char instead of strings?

        public string TmcId { get; set; }
        public readonly List<string> TimeStamps = new List<string>();
        public readonly List<double> Speeds = new List<double>();
        public readonly List<double> AvgSpeeds = new List<double>();
        public readonly List<double> RefSpeeds = new List<double>();
        public readonly List<double> TravelTimes = new List<double>();
        public readonly List<string> DataDensities = new List<string>();
    }
}