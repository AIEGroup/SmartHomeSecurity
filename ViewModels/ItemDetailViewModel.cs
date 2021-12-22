using SmartSecurity.Models;
using System;
using System.Diagnostics;
using System.IO;
using System.Threading.Tasks;
using Xamarin.Forms;

namespace SmartSecurity.ViewModels
{
    [QueryProperty(nameof(ItemId), nameof(ItemId))]
    public class ItemDetailViewModel : BaseViewModel
    {
        private string itemId;
        private string date;
        private string description;
        public ImageSource isource;
        private string test;
        public string Id { get; set; }

        public string Test
        {
            get => test;
            set => SetProperty(ref test, value);
        }

        public string Date
        {
            get => date;
            set => SetProperty(ref date, value);
        }

        public string Description
        {
            get => description;
            set => SetProperty(ref description, value);
        }

        public ImageSource IS
        {
            get => isource;
            set => SetProperty(ref isource, value);
        }

        public string ItemId
        {
            get
            {
                return itemId;
            }
            set
            {
                itemId = value;
                LoadItemId(value);
            }
        }

        public async void LoadItemId(string itemId)
        {
            try
            {
                var item = await DataStore.GetItemAsync(itemId);
                Id = item.Id;
                Date = item.Date;
                Description = item.Description;
                Test = "Hello World";
                byte[] bytes = Convert.FromBase64String("");
                var data = ImageSource.FromStream(() => new MemoryStream(bytes));
                IS = item.Source;
                Debug.WriteLine("Value: " + IS);

            }
            catch (Exception)
            {
                Debug.WriteLine("Failed to Load Item");
            }
        }
    }
}
