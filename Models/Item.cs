using System;
using Xamarin.Forms;

namespace SmartSecurity.Models
{
    public class Item
    {
        public string Id { get; set; }
        public string Date { get; set; }
        public string Description { get; set; }
        public ImageSource Source { get; set; }
    }
}