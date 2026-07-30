using System.Collections.Concurrent;
using System.Text.Json;

namespace Day03.Memory;

public class MemoryEntry
{
    public string Id { get; set; } = "";
    public string Text { get; set; } = "";
    public Dictionary<string, string> Metadata { get; set; } = new();
    public DateTime CreatedAt { get; set; } = DateTime.UtcNow;
}

public class MemoryStore
{
    private readonly ConcurrentDictionary<string, MemoryEntry> _store = new();
    private readonly string _filePath;

    public MemoryStore(string? filePath = null)
    {
        _filePath = filePath ?? Path.Combine(AppContext.BaseDirectory, "memory.json");
        LoadFromFile();
    }

    public void Save(string id, string text, Dictionary<string, string>? metadata = null)
    {
        _store[id] = new MemoryEntry
        {
            Id = id,
            Text = text,
            Metadata = metadata ?? new Dictionary<string, string>(),
            CreatedAt = DateTime.UtcNow
        };
        SaveToFile();
    }

    public MemoryEntry? Retrieve(string id)
    {
        _store.TryGetValue(id, out var entry);
        return entry;
    }

    public List<MemoryEntry> Search(string query, int k = 5)
    {
        var queryWords = query.ToLower().Split(' ', StringSplitOptions.RemoveEmptyEntries);
        return _store.Values
            .Select(entry => new
            {
                Entry = entry,
                Score = ComputeSimilarity(queryWords, entry.Text.ToLower().Split(' ', StringSplitOptions.RemoveEmptyEntries))
            })
            .Where(x => x.Score > 0)
            .OrderByDescending(x => x.Score)
            .Take(k)
            .Select(x => x.Entry)
            .ToList();
    }

    public void Update(string id, string text, Dictionary<string, string>? metadata = null)
    {
        if (_store.TryGetValue(id, out var existing))
        {
            existing.Text = text;
            if (metadata != null) existing.Metadata = metadata;
            SaveToFile();
        }
    }

    public void Delete(string id)
    {
        _store.TryRemove(id, out _);
        SaveToFile();
    }

    public int Count() => _store.Count;

    private double ComputeSimilarity(string[] words1, string[] words2)
    {
        if (words1.Length == 0 && words2.Length == 0) return 0;
        var intersection = words1.Intersect(words2).Count();
        var union = words1.Union(words2).Count();
        return union == 0 ? 0 : (double)intersection / union;
    }

    private void SaveToFile()
    {
        try
        {
            var dir = Path.GetDirectoryName(_filePath);
            if (!string.IsNullOrEmpty(dir) && !Directory.Exists(dir))
                Directory.CreateDirectory(dir);
            var json = JsonSerializer.Serialize(_store.Values.ToList());
            File.WriteAllText(_filePath, json);
        }
        catch { }
    }

    private void LoadFromFile()
    {
        try
        {
            if (File.Exists(_filePath))
            {
                var json = File.ReadAllText(_filePath);
                var entries = JsonSerializer.Deserialize<List<MemoryEntry>>(json);
                if (entries != null)
                    foreach (var e in entries)
                        _store[e.Id] = e;
            }
        }
        catch { }
    }
}
