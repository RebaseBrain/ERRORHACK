﻿using System.Text.RegularExpressions;
using Entities;
using Services;
using System.Text.Json;

class Program
{
    static async Task Main()
    {
        string logUrl = "https://rdb.altlinux.org/api/export/beehive/ftbfs?branch=sisyphus";

        HttpClient client = new HttpClient();
        string logContent = await client.GetStringAsync(logUrl);
        var urls = Regex.Matches(logContent, @"https?://[^\s""'>]+")
                .Select(m => m.Value)
                .ToList();
        var abobas = JsonSerializer.Deserialize<FtbfsResponse>(logContent);

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
            Console.WriteLine("Логи ошибок не найдены!");
        }
    }
}
