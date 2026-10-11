param(
    [string]$Config = "config/default.json",
    [string]$Topology,
    [string]$SeedNode,
    [double]$Beta,
    [int]$Budget,
    [int]$Trials,
    [int]$RandomSeed
)

$scriptArgs = @("-m", "src.comparison", "--config", $Config)

if ($PSBoundParameters.ContainsKey("Topology")) {
    $scriptArgs += @("--topology", $Topology)
}
if ($PSBoundParameters.ContainsKey("SeedNode")) {
    $scriptArgs += @("--seed-node", $SeedNode)
}
if ($PSBoundParameters.ContainsKey("Beta")) {
    $scriptArgs += @("--beta", $Beta)
}
if ($PSBoundParameters.ContainsKey("Budget")) {
    $scriptArgs += @("--budget", $Budget)
}
if ($PSBoundParameters.ContainsKey("Trials")) {
    $scriptArgs += @("--trials", $Trials)
}
if ($PSBoundParameters.ContainsKey("RandomSeed")) {
    $scriptArgs += @("--random-seed", $RandomSeed)
}

python @scriptArgs
