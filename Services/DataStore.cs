using Newtonsoft.Json;
using SmartSecurity.Models;
using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.IO;
using System.Linq;
using System.Net.Http;
using System.Threading.Tasks;
using Xamarin.Forms;

namespace SmartSecurity.Services
{
    public class DataStore : IDataStore<Item>
    {
        private List<Item> items = new List<Item>();
        //delegates
        public delegate void DataDownloadedEventHandler(object sender, EventArgs e);

        //events
        public static event DataDownloadedEventHandler DataDownloaded;

        public async void GetItems()
        {
            using (HttpClient client = new HttpClient())
            {
                string url = "http://77.55.211.131:4000/test/";
                var input = await client.GetAsync(url);

                OnDataDownloaded();

                List<Photo> photos = JsonConvert.DeserializeObject<List<Photo>>(input.Content.ReadAsStringAsync().Result);

                foreach (var item in photos)
                {
                    byte[] bytes = Convert.FromBase64String(item.BASE);
                    var data = ImageSource.FromStream(() => new MemoryStream(bytes));

                    items.Add(new Item { Id = Convert.ToString(item.ID), Text = "Text", Description = item.DESCRIPTION, Source = data });
                }

                Debug.WriteLine(items[0].Source);
            }
        }

        public DataStore()
        {
            GetItems();
        }

        public async Task<bool> AddItemAsync(Item item)
        {
            items.Add(item);

            return await Task.FromResult(true);
        }

        public async Task<bool> UpdateItemAsync(Item item)
        {
            var oldItem = items.Where((Item arg) => arg.Id == item.Id).FirstOrDefault();
            items.Remove(oldItem);
            items.Add(item);

            return await Task.FromResult(true);
        }

        public async Task<bool> DeleteItemAsync(string id)
        {
            var oldItem = items.Where((Item arg) => arg.Id == id).FirstOrDefault();
            items.Remove(oldItem);

            return await Task.FromResult(true);
        }

        public async Task<Item> GetItemAsync(string id)
        {
            return await Task.FromResult(items.FirstOrDefault(s => s.Id == id));
        }

        public async Task<IEnumerable<Item>> GetItemsAsync(bool forceRefresh = false)
        {
            return await Task.FromResult(items);
        }

        protected virtual void OnDataDownloaded()
        {
            DataDownloaded(this, EventArgs.Empty);
        }
    }
}