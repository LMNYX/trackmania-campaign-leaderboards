var scores_json;
var maps_json;
var actualScores = {};
var bestScores = {};

window.onload = async function ()
{
    var maps = await fetch('/api/get_maps');
    maps_json = await maps.json();

    for (var i = 0; i < maps_json.length; i++)
    {
        var map = document.createElement('div');
        map.classList.add('map');
        map.setAttribute('data-id', maps_json[i].id);

        var img = document.createElement('img');
        img.src = maps_json[i].thumbnail;

        var contents = document.createElement('div');
        contents.classList.add('contents');

        var header = document.createElement('span');
        header.classList.add('header');
        header.innerText = maps_json[i].name;

        var holder = document.createElement('span');
        holder.classList.add('holder');

        var username = document.createElement('span');
        username.classList.add('username');
        username.innerText = "Loading...";

        var medal = document.createElement('img');
        medal.src = '/public/imgs/medals/author.png';

        var time = document.createElement('span');
        time.classList.add('time');
        time.innerText = "Loading...";

        holder.appendChild(username);
        holder.appendChild(medal);
        holder.appendChild(time);

        contents.appendChild(header);
        contents.appendChild(holder);

        map.appendChild(img);
        map.appendChild(contents);

        map.onclick = function () { ShowLeaderboard(this.getAttribute('data-id')); };

        document.querySelector('.main').appendChild(map);
    };

    var scores = await fetch('/api/get_scores');
    scores_json = await scores.json();

    for (const [key, value] of Object.entries(scores_json))
    {
        for (const [mapKey, mapValue] of Object.entries(value))
        {
            if (actualScores[mapKey] == undefined)
            {
                actualScores[mapKey] = {};
            }

            if (actualScores[mapKey][key] == undefined)
            {
                actualScores[mapKey][key] = {};
            }

            actualScores[mapKey][key] = mapValue;
            actualScores[mapKey][key].username = key;
        }
    }

    // compare actual scores
    for (const [key, value] of Object.entries(actualScores))
    {
        var bestTime = 0;
        var bestUsername = "";
        for (const [username, time] of Object.entries(value))
        {
            if (bestTime == 0)
            {
                bestTime = time.time;
                bestUsername = username;
            }
            if (time.time < bestTime)
            {
                bestTime = time.time;
                bestUsername = username;
            }
        }

        if ( !(key in bestScores) )
        {
            bestScores[key] = {};
        }

        bestScores[key] = actualScores[key][bestUsername];
        bestScores[key].username = bestUsername;
    }

    // set best scores
    for (const [key, value] of Object.entries(bestScores))
    {
        var map = document.querySelector(`div.map[data-id="${key}"]`);
        map.querySelector('span.username').innerText = value.username;
        // convert seconds to mm:ss
        var seconds = parseInt(value.time)/1000;

        var minutes = Math.floor(seconds / 60);
        seconds = seconds - (minutes * 60);
        seconds = seconds.toFixed(3);

        if (seconds < 10)
        {
            seconds = `0${seconds}`;
        }
        if (minutes < 10)
        {
            minutes = `0${minutes}`;
        }



        seconds = `${minutes > 0 ? minutes+':' : ''}${seconds}`;

        map.querySelector('span.time').innerText = seconds;

        var medalImg = map.querySelector(`div.map[data-id="${key}"] > .contents > .holder > img`);

        switch (value.medal)
        {
            case 0:
                medalImg.src = '/public/imgs/medals/none.png';
                break;
            case 1:
                medalImg.src = '/public/imgs/medals/bronze.png';
                break;
            case 2:
                medalImg.src = '/public/imgs/medals/silver.png';
                break;
            case 3:
                medalImg.src = '/public/imgs/medals/gold.png';
                break;
            case 4:
                medalImg.src = '/public/imgs/medals/author.png';
                break;
            default: break;
        }
    }

    anime({
        targets: 'div.loader',
        opacity: 0,
        duration: 1000,
        easing: 'linear',
        complete: function (anim) {
            document.querySelector('div.loader').style.display = 'none'
        }
    });

    var _scores = {};
    for (const [key, value] of Object.entries(bestScores))
    {
        if (_scores[value.username] == undefined)
        {
            _scores[value.username] = 1;
        }
        else
        {
            _scores[value.username]++;
        }
    }

    // sort _scores
    _scores = Object.fromEntries(
        Object.entries(_scores).sort(([, a], [, b]) => b - a)
    );

    var globalLeaderboard = document.querySelector('div#global-leaderboard');
    var i = 0;
    for (const [key, value] of Object.entries(_scores))
    {
        var entry = document.createElement('div');
        entry.classList.add('leaderboard-entry');

        var rank = document.createElement('span');
        rank.classList.add('rank');
        rank.innerText = i + 1;

        var username = document.createElement('span');
        username.classList.add('username');
        username.innerText = key;

        var time = document.createElement('span');
        time.classList.add('time');
        time.innerText = value;

        entry.appendChild(rank);
        entry.appendChild(username);
        entry.appendChild(time);

        globalLeaderboard.appendChild(entry);
        i++;
    }

    document.querySelector('.blurer').onclick = function () { HideLeaderboard(); };
}

function ShowLeaderboard(mapId)
{
    document.querySelector('div.fixed-leaderboard').style.display = 'block';
    document.querySelector('div.blurer').style.display = 'block';
    anime({
        targets: 'div.blurer',
        opacity: 1,
        duration: 200,
        easing: 'linear'
    });
    anime({
        targets: 'div.fixed-leaderboard',
        opacity: 1,
        duration: 200,
        easing: 'linear'
    });

    // find map in maps_json with id
    var _map = maps_json.find(function (__map) { return __map.id == mapId; });

    document.querySelector('div.fixed-leaderboard > .banner > span').innerText = _map.name;
    document.querySelector('div.fixed-leaderboard > .banner > .image').src = _map.thumbnail;

    var leaderboard = document.querySelector('div.fixed-leaderboard > .leaderboard-entries');

    leaderboard.innerHTML = "";

    var scores = actualScores[mapId];

    var _scores = [];

    for (const [username, score] of Object.entries(scores)) {
        _scores.push(score);
    }

    _scores.sort(function (a, b) { return a.time - b.time; });
    console.log(_scores);

    for (var i = 0; i < _scores.length; i++)
    {
        var score = _scores[i];
        console.log(score.username);

        var entry = document.createElement('div');
        entry.classList.add('leaderboard-entry');

        var rank = document.createElement('span');
        rank.classList.add('rank');
        rank.innerText = i + 1;

        var username = document.createElement('span');
        username.classList.add('username');
        username.innerText = score.username;

        var time = document.createElement('span');
        time.classList.add('time');
        // convert seconds to mm:ss
        var seconds = parseInt(score.time) / 1000;

        var minutes = Math.floor(seconds / 60);
        seconds = seconds - (minutes * 60);
        seconds = seconds.toFixed(3);

        if (seconds < 10) {
            seconds = `0${seconds}`;
        }
        if (minutes < 10) {
            minutes = `0${minutes}`;
        }

        seconds = `${minutes > 0 ? minutes + ':' : ''}${seconds}`;

        time.innerText = seconds;

        var medal = document.createElement('img');
        medal.classList.add('medal');
        switch (score.medal)
        {
            case 0:
                medal.src = '/public/imgs/medals/none.png';
                break;
            case 1:
                medal.src = '/public/imgs/medals/bronze.png';
                break;
            case 2:
                medal.src = '/public/imgs/medals/silver.png';
                break;
            case 3:
                medal.src = '/public/imgs/medals/gold.png';
                break;
            case 4:
                medal.src = '/public/imgs/medals/author.png';
                break;
            default: break;
        }

        entry.appendChild(medal);

        entry.appendChild(rank);
        entry.appendChild(username);
        entry.appendChild(time);

        leaderboard.appendChild(entry);
    }

    document.querySelector('div.fixed-leaderboard > .close-leaderboard').addEventListener('click', function () {
        HideLeaderboard();
    });
    
}

function HideLeaderboard()
{
    anime({
        targets: 'div.blurer',
        opacity: 0,
        duration: 200,
        easing: 'linear',
        complete: function (anim)
        {
            document.querySelector('div.blurer').style.display = 'none'
        }
    });
    anime({
        targets: 'div.fixed-leaderboard',
        opacity: 0,
        duration: 200,
        easing: 'linear',
        complete: function (anim)
        {
            document.querySelector('div.fixed-leaderboard').style.display = 'none'
        }
    });
}