using System.Text.RegularExpressions;
using Entities;
using Services;
using System.Text.Json;
using TF_IDF;

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

		Console.WriteLine(Python.ExecutePythonScript("../test.py", ""));

		if (abobas?.Ftbfs != null)
		{
			foreach (var aboba in abobas.Ftbfs)
			{
				try
				{
					HttpResponseMessage response = await client.GetAsync(aboba.Url);

					if (response.IsSuccessStatusCode)
					{
						string logs = await response.Content.ReadAsStringAsync();
						string errors = LogsCleaner.ExtractErrors(logs);
						await File.WriteAllTextAsync($"./logs/{aboba.Name}.txt", logs);
						await File.WriteAllTextAsync($"./errors/{aboba.Name}.txt", errors);
					}
				}
				catch (Exception ex)
				{
					Console.WriteLine($"Can not write file {aboba.Name}: {ex.Message}");
				}
			}
		}
		else
		{
			Console.WriteLine("У вас абоба нулёвая");
		}
	}
}
