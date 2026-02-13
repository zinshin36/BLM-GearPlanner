using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text.Json;
using System.Windows;
using System.Windows.Controls;

namespace BLMRotationSim
{
    public partial class MainWindow : Window
    {
        Dictionary<string, List<GearPiece>> gearPool = new();

        public MainWindow()
        {
            InitializeComponent();
            LoadGear();
        }

        private void LoadGear()
        {
            string path = "data/gear.json";
            string json = File.ReadAllText(path);
            gearPool = JsonSerializer.Deserialize<Dictionary<string, List<GearPiece>>>(json);

            // Fill dropdowns
            HeadDropdown.ItemsSource = gearPool["Head"].Select(g => g.Name);
            HeadDropdown.SelectedIndex = 0;

            BodyDropdown.ItemsSource = gearPool["Body"].Select(g => g.Name);
            BodyDropdown.SelectedIndex = 0;
        }

        private void Simulate_Click(object sender, RoutedEventArgs e)
        {
            int crit = int.Parse(CritBox.Text);
            int dh = int.Parse(DhBox.Text);
            int det = int.Parse(DetBox.Text);
            int sps = int.Parse(SpsBox.Text);

            // Apply selected gear
            var selectedGear = new List<GearPiece>
            {
                gearPool["Head"].First(g => g.Name == (string)HeadDropdown.SelectedItem),
                gearPool["Body"].First(g => g.Name == (string)BodyDropdown.SelectedItem)
            };

            foreach (var g in selectedGear)
            {
                crit += g.Crit;
                dh += g.DirectHit;
                det += g.Determination;
                sps += g.SpellSpeed;
            }

            double dps = RotationSimulator.CalculateDPS(crit, dh, det, sps);

            ResultText.Text = $"Estimated DPS: {dps:F2}\nGear: {selectedGear[0].Name}, {selectedGear[1].Name}";
        }

        private void Gear_SelectionChanged(object sender, SelectionChangedEventArgs e)
        {
            // Optional: auto-update DPS on change
        }
    }

    public class GearPiece
    {
        public string Name { get; set; }
        public int Crit { get; set; }
        public int DirectHit { get; set; }
        public int Determination { get; set; }
        public int SpellSpeed { get; set; }
    }

    static class RotationSimulator
    {
        const int BaseSub = 400;
        const int LevelDiv = 1900;

        public static double CalculateDPS(int crit, int dh, int det, int sps)
        {
            double gcd = CalculateGCD(sps);
            double time = 60.0;
            double casts = time / gcd;
            double potency = casts * 310;
            double multiplier = DamageMultiplier(crit, dh, det, sps);
            return potency / time * multiplier;
        }

        static double CalculateGCD(int sps)
        {
            int reduction = (int)Math.Floor(130.0 * (sps - BaseSub) / LevelDiv);
            return (2500 - reduction) / 1000.0;
        }

        static double DamageMultiplier(int crit, int dh, int det, int sps)
        {
            double critRate = Math.Floor(200.0 * (crit - BaseSub) / LevelDiv + 50) / 1000.0;
            double critBonus = Math.Floor(200.0 * (crit - BaseSub) / LevelDiv + 1400) / 1000.0;
            double dhRate = Math.Floor(550.0 * (dh - BaseSub) / LevelDiv) / 1000.0;
            double detBonus = Math.Floor(140.0 * (det - BaseSub) / LevelDiv + 1000) / 1000.0;
            double spsBonus = 1.0 + (sps - BaseSub) / 10000.0;
            return detBonus * (1 + critRate * (critBonus - 1)) * (1 + dhRate * 0.25) * spsBonus;
        }
    }
}
