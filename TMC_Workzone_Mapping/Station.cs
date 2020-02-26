namespace TMC_Workzone_Mapping
{
    public class Station
    {
        public string Corridor { get; set; }
        public string Direction { get; set; }
        public string Id { get; set; }
        public double Lon { get; set; }
        public double Lat { get; set; }


        // public List<Detector> Detectors = new List<Detector>();

        public override string ToString()
        {
            return $"Corridor[{Corridor}] Direction[{Direction}]\n" +
                   $"StationId[{Id}] Lon[{Lon}] Lat[{Lat}]";
        }
    }

    // public class Detector
    // {
    //     public double Lat { get; set; }   
    //     public double Long { get; set; }
    //     public override string ToString()
    //     {
    //         return $"Detector Lat[{Lat}] Long[{Long}]";
    //     }
    // }
}