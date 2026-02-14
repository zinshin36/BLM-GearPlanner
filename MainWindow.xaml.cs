using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text.Json;
using System.Windows;

namespace BLMRotationSim
{
    public partial class MainWindow : Window
    {
        private Dictionary<string, List<GearPiece>> gearPool = new();
        private readonly string logPath = "runtime_log.txt";

        public MainWindow()
        {
            InitializeComponent();
            Log("Application started.");
            LoadGear();
        }

        private void Log(string message)
        {
            File.AppendAllText(logPath, $"{DateTime.Now}: {message}\n");
        }

        private void LoadGear()
        {
            try
            {
                string path = "data/gear.json";

                if (!File.Exists(path))
                {
                    Log("gear.json not found.");
                    MessageBox.Show("gear.json not found.");
                    return;
                }

                string json = File.ReadAllText(path);

                gearPool = JsonSerializer.Deserialize<Dictionary<string, List<GearPiece>>>(json)
                           ?? new Dictionary<string, List<GearPiece>>();

                if (gearPool.ContainsKey("Head"))
                {
                    HeadDropdown.ItemsSource = gearPool["Head"].Select(g => g.Name).ToList();
                    HeadDropdown.SelectedIndex = 0;
                }

                if (gearPool.ContainsKey("Body"))
                {
                    BodyDropdown.ItemsSource = gearPool["Body"].Select(g => g.Name).ToList();
                    BodyDropdown.SelectedIndex = 0;
                }

                Log("Gear loaded successfully.");
            }
            catch (Exception ex)
            {
                Log("LoadGear ERROR: " + ex.ToString());
                MessageBox.Show("Error loading gear. Check runtime_log.txt");
            }
        }

        private void Simulate_Click(object sender, RoutedEventArgs e)
        {
            try
            {
                int crit = int.Parse(CritBox.Text ?? "0");
                int dh = int.Parse(DhBox.Text ?? "0");
                int det = int.Parse(DetBox.Text ?? "0");
                int sps = int.Parse(SpsBox.Text ?? "0");

                if (HeadDropdown.SelectedItem == null || BodyDropdown.SelectedItem == null)
                {
                    MessageBox.Show("Select gear first.");
                    return;
                }

                var selectedGear = new List<GearPiece>
                {
                    gearPool["Head"].First(g => g.Name == HeadDropdown.SelectedItem!.ToString()),
                    gearPool["Body"].First(g => g.Name == BodyDropdown.SelectedItem!.ToString())
                };

                foreach (var g in selectedGear)
                {
                    crit += g.Crit;
                    dh += g.DirectHit;
                    det += g.Determination;
                    sps += g.SpellSpeed;
                }

                double dps = RotationSimulator.CalculateDPS(crit, dh, det, sps);

                ResultText.Text = $"Estimated DPS: {dps:F2}";
                Log($"Simulation complete. DPS: {dps:F2}");
            }
            catch (Exception ex)
            {
                Log("Simulate ERROR: " + ex.ToString());
                MessageBox.Show("Simulation failed. Check runtime_log.txt");
            }
        }
    }

    public class GearPiece
    {
        public string Name { get; set; } = "";
        public int Crit { get; set; }
        public int DirectHit { get; set; }
        public int Determination { get; set; }
        public int SpellSpeed { get; set; }
    }

    public static class RotationSimulator
    {
        private const int BaseSub = 400;
        private const int LevelDiv = 1900;

        public static double CalculateDPS(int crit, int dh, int det, int sps)
        {
            double gcd = Calcula
