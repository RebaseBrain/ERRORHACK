using System.Text.RegularExpressions;

namespace Services;

public static class LogsCleaner
{
    static readonly Regex ErrorRegex = new Regex(
        @"(
			\berror[:\s]                |   # C/C++/GCC, Python, etc.
			\bfatal\s+error             |   # C/C++
			\bundefined\s+reference     |   # Linking errors
			\bsegmentation\s+fault      |   # Runtime
			\bexception\b               |   # Python/Java/etc.
			\btraceback\b               |   # Python
			\bfailed\b                  |   # General failure
			\bNo\s+such\s+file          |   # Missing includes/files
			\bcommand\s+not\s+found     |   # Shell errors
			\bundefined\s+symbol        |   # Linker
			\bE:\s                      |   # Debian/apt style
			\bFATAL:                    |   # Systemd/logs
			\bFAIL\b                    |   # Build scripts/tests
			\bfail:                     |   # Build logs
			\bError\s+\d{3}             # e.g., HTTP/compilation codes
		)",
        RegexOptions.IgnoreCase | RegexOptions.IgnorePatternWhitespace | RegexOptions.Compiled
    );

    public static string ExtractErrors(string logText, int contextRadius = 10)
    {
        var lines = logText.Split('\n');

        var contextLineIndices = Enumerable.Range(0, lines.Length)
            .Where(i => ErrorRegex.IsMatch(lines[i]))
            .SelectMany(i =>
                Enumerable.Range(
                    Math.Max(0, i - contextRadius),
                    Math.Min(lines.Length - Math.Max(0, i - contextRadius), contextRadius * 2 + 1)
                )
            )
            .OrderBy(i => i); // оставляем порядок появления

        var resultLines = contextLineIndices.Select(i => lines[i]);

        return string.Join('\n', resultLines);
    }
}
