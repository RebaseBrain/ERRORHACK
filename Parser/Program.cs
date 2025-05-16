using System.Text.RegularExpressions;
using Entities;
using System.Text.Json;

class Program
{
	static async Task Main()
	{
		string logUrl = "https://rdb.altlinux.org/api/export/beehive/ftbfs?branch=sisyphus";

		HttpClient client = new HttpClient();
		string logContent = await client.GetStringAsync(logUrl);
		//logContent = "https://asdas asd httd a https://dsadad";
		var urls = Regex.Matches(logContent, @"https?://[^\s""'>]+")
				.Select(m => m.Value)
				.ToList();
		var abobas = JsonSerializer.Deserialize<FtbfsResponse>(logContent);


		if (abobas?.Ftbfs != null)
		{
			foreach (var aboba in abobas.Ftbfs)
			{
				var errors = await client.GetStringAsync(aboba.Url);
				Console.WriteLine(errors);
			}
		}
		else
		{
			Console.WriteLine("У вас абоба нулёвая");
		}
	}
}
