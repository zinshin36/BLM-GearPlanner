using System.Windows;

namespace BLMRotationSim
{
    public partial class App : Application
    {
        [System.STAThreadAttribute()]
        public static void Main()
        {
            App app = new App();
            app.InitializeComponent();
            app.Run();
        }
    }
}
