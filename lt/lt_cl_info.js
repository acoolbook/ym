/*
22 0,20 * * * caoliu论坛信息查询
*/
const $ = new Env("小草信息查询");
const notify = $.isNode() ? require('./sendNotify') : '';
let clcookie = '', clcookiesArr = [], cookie = '', message = '', username='',level='',ww='',ip='',lastlogintime='',money='',gx='',tz='',newmessagetitle='',newmessagecontent='',newmessageauthor='',newmessagetime='';
let hqck='',hqlx='',hqcktime='',dqck='',dqlx='',dqcktime='',dqdqtime='',allmoney='',isnewmessage,newmessageurl,newmessageurlold=''
let ismessage
if (process.env.clcookie) {
  if (process.env.clcookie.indexOf('&') > -1) {
    clcookiesArr = process.env.clcookie.split('&');
  } else if (process.env.clcookie.indexOf('\n') > -1) {
    clcookiesArr = process.env.clcookie.split('\n');
  } else {
    clcookiesArr = [process.env.clcookie];
  }
}
let time = new Date()
if (process.env.clua) {
    UA = process.env.clua
}
!(async () => {
    if (!clcookiesArr[0]) {
        $.msg($.name, '请先添加cookie');
        return;
    }
    if (!UA) {
        console.log('需手动抓取ua才可运行,且需保证cookie与ua对应')
        return;
    }
    console.log("共" + clcookiesArr.length + "个账号")
    ismessage = false
    for (let i = 0; i < clcookiesArr.length; i++) {
        if (clcookiesArr[i]) {
            cookie = clcookiesArr[i]
            $.index = i + 1;
            $.nickName = '';
            islogin = true
            isnewmessage = true
            newmessageurl=''
            console.log(`\n******开始【账号${$.index}】*********\n`);
            await getbaseinfo()
            if (!islogin) {               
                continue
            }
            await $.wait(2000)
            await getbankinfo()
            await $.wait(1500)
            let js=0            
            while (isnewmessage && js<5) {                
                //console.log(isnewmessage)
                await $.wait(1500)
                js += 1
                await getmesssage()
                //console.log(newmessageurl)
                if (newmessageurl === newmessageurlold) {
                    break;
                }
                if (newmessageurl) {
                    console.log('第'+js+'次查看消息')
                    await $.wait(1500)                    
                    await getreadmessage(newmessageurl, js)
                    newmessageurlold = newmessageurl
                    await $.wait(1500)                      
                }
            }              
        }
    }
    console.log(new Date().getHours())
    if (message !== '' && (ismessage || time.getHours()  == 21)) {
        
        if ($.isNode()) {
            await notify.sendNotify($.name, message, '', `\n`);
        } else {
            $.msg($.name, '', message);
        }
    }
})()
    .catch((e) => {
        $.log('', `❌ ${$.name}, 失败! 原因: ${e}!`, '')
    })
    .finally(() => {
        $.done();
    })

async function getmesssage() {
    return new Promise(resolve => {
        $.get(geturl('message.php'), (err, resp, data) => {
            try {
                if (err) {
                    $.logErr(err)
                } else {
                    if (data) {
                        //console.log(data)
                        if (data.indexOf('您的信箱已滿') != -1) {
                            console.log('有新消息但查看失败，信箱已满,无法查看，请手动删除部分消息')
                            isnewmessage = false
                            ismessage = true
                            return;

                        }
                       if (data.indexOf('否') != -1) {
                           newmessagetime = /\<td class\=\"tac\"\>(.+?)\<\/td\>\s+.+?\s+\<font color\=\"red\"\>否/.exec(data)[1]
                           newmessageauthor = /uid\=(\d+)\"\>(.+?)\<\/a\>\<\/td\>\s+.+?\s+.+?\s+.+?\s+\<font color\=\"red\"\>否/.exec(data)[2]
                           newmessagetitle = /mid=(\d+)\"\>(.+?)\<\/a\>\s+.+?\s+.+?\s+.+?\s+.+?\s+.+?\s+\<font color\=\"red\"\>否/.exec(data)[2]
                           newmessageurl = /href\=\"(.+?)\"\>.+?\s+.+?\s+.+?\s+.+?\s+.+?\s+.+?\s+\<font color\=\"red\"\>否/.exec(data)[1]
                           isnewmessage = true    
                           ismessage = true                  
                           console.log('有新消息，尝试去查看')
                           return                            
                        } else {
                            isnewmessage = false
                        }

                    }
                }
            } catch (e) {
                $.logErr(e)
            } finally {
                resolve();
            }
        })
            
    })  

}

async function getreadmessage(newmessageurl,js) {
    return new Promise(resolve => {
        $.get(geturl(newmessageurl), (err, resp, data) => {
            try {
                if (err) {
                    $.logErr(err)
                } else {
                    if (data) {
                        //console.log(data)
                        newmessagecontent = /content\'\>(.+?)\</.exec(data)[1]
                        //console.log(newmessagecontent)
                        console.log(`新消息${js}来自：${newmessageauthor}\n标题：${newmessagetitle}\n内容：${newmessagecontent}\n时间：${newmessagetime}`)
                        message += `新消息${js}来自：${newmessageauthor}\n标题：${newmessagetitle}\n内容：${newmessagecontent}\n时间：${newmessagetime}\n\n`

                    }
                }
                
            } catch (e) {
                $.logErr(e)
            } finally {
                resolve();
            }
        })
    })      
}

async function getbaseinfo() {
    return new Promise(resolve => {
        $.get(geturl('index.php'), (err, resp, data) => {
            try {
                if (err) {
                    $.logErr(err)
                } else {
                    if (data) {
                        //console.log('基础信息'+data)
                        if (data.indexOf('您尚未') != -1) {
                           console.log(`账号${$.index}cookie已失效，请重新抓取`)
                           islogin = false 
                           message += `账号${$.index}cookie已失效，请重新抓取\n\n`
                           return
                        }
                       
                       username = /font-weight\:bold\"\>(.+?)\</.exec(data)[1]
                       level = /span class\=\"s3\"\>(.+?)\</.exec(data)[1]
                       lastlogintime = /上次登錄時間\:(.+?)\|/.exec(data)[1]
                       ip = /您的IP \:(.+?)\</.exec(data)[1]
                       ww = /威望\:(.+?)\|/.exec(data)[1]
                       money = /金錢\:(.+?)\|/.exec(data)[1]
                       gx = /貢獻\:(.+?)\|/.exec(data)[1]
                       tz = /共發表帖子\:(.+?)\|/.exec(data)[1]
                       console.log(`用户${$.index}：${username}\n等级：${level}\n上次登录时间：${lastlogintime}\n当前IP：${ip}\n威望：${ww}\n金钱：${money}\n贡献：${gx}\n共发表帖子：${tz}\n`)
                       message += `用户${$.index}：${username}\n等级：${level}\n上次登录时间：${lastlogintime}\n当前IP：${ip}\n威望：${ww}\n金钱：${money}\n贡献：${gx}\n共发表帖子：${tz}\n`

                    }
                }
            } catch (e) {
                $.logErr(e)
            } finally {
                resolve();
            }
        })
    })
}

async function getbankinfo() {
    return new Promise(resolve => {
        $.get(geturl("hack.php?H_name=bank"), (err, resp, data) => {
            try {
                if (err) {
                    $.logErr(err)
                } else {
                    if (data) {
                        //console.log(data)
                        hqck = /活期存款：(.+?)\</.exec(data)[1]
                        hqlx = /利息：(.+?)\</.exec(data)[1]
                        hqcktime = /\>存款时间(.+?)\</.exec(data)[1]
                        dqck = /定期存款：(.+?)\</.exec(data)[1]
                        dqlx = /定期存款：.+?　　利息：(.+?)\</.exec(data)[1]
                        dqcktime = /定期存款：.+?存款时间：(.+?)\</.exec(data)[1]
                        dqdqtime = /到期时间：(.+?)\</.exec(data)[1]
                        allmoney = /总资产：(.+?)USD/.exec(data)[1]
                        //dqck = /定期存款：(.+?)\</.exec(data)[1]
                        console.log(`活期存款：${hqck}\n活期利息：${hqlx}\n活期存款时间：${hqcktime}\n定期存款：${dqck}\n定期利息：${dqlx}\n定期存款时间：${dqcktime}\n定期到期时间：${dqdqtime}\n总资产：${allmoney}\n`)
                        message += `活期存款：${hqck}\n活期利息：${hqlx}\n活期存款时间：${hqcktime}\n定期存款：${dqck}\n定期利息：${dqlx}\n定期存款时间：${dqcktime}\n定期到期时间：${dqdqtime}\n总资产：${allmoney}\n\n`
                      
                    }
                }
            } catch (e) {
                $.logErr(e)
            } finally {
                resolve();
            }
        })
    })
}

function geturl(url) {
    const options = {
        url: "http://t66y.com/" + url,
        headers: {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Cookie': cookie,
            'DNT': '1',
            'Host': 't66y.com',
            'Proxy-Connection': 'keep-alive',
            'Referer': 'http://t66y.com/index.php',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': UA,

        }
    };
    //console.log(cookie)
    return options

}



// prettier-ignore

function Env(t, e) { "undefined" != typeof process && JSON.stringify(process.env).indexOf("GITHUB") > -1 && process.exit(0); class s { constructor(t) { this.env = t } send(t, e = "GET") { t = "string" == typeof t ? { url: t } : t; let s = this.get; return "POST" === e && (s = this.post), new Promise((e, i) => { s.call(this, t, (t, s, r) => { t ? i(t) : e(s) }) }) } get(t) { return this.send.call(this.env, t) } post(t) { return this.send.call(this.env, t, "POST") } } return new class { constructor(t, e) { this.name = t, this.http = new s(this), this.data = null, this.dataFile = "box.dat", this.logs = [], this.isMute = !1, this.isNeedRewrite = !1, this.logSeparator = "\n", this.startTime = (new Date).getTime(), Object.assign(this, e), this.log("", `🔔${this.name}, 开始!`) } isNode() { return "undefined" != typeof module && !!module.exports } isQuanX() { return "undefined" != typeof $task } isSurge() { return "undefined" != typeof $httpClient && "undefined" == typeof $loon } isLoon() { return "undefined" != typeof $loon } toObj(t, e = null) { try { return JSON.parse(t) } catch { return e } } toStr(t, e = null) { try { return JSON.stringify(t) } catch { return e } } getjson(t, e) { let s = e; const i = this.getdata(t); if (i) try { s = JSON.parse(this.getdata(t)) } catch { } return s } setjson(t, e) { try { return this.setdata(JSON.stringify(t), e) } catch { return !1 } } getScript(t) { return new Promise(e => { this.get({ url: t }, (t, s, i) => e(i)) }) } runScript(t, e) { return new Promise(s => { let i = this.getdata("@chavy_boxjs_userCfgs.httpapi"); i = i ? i.replace(/\n/g, "").trim() : i; let r = this.getdata("@chavy_boxjs_userCfgs.httpapi_timeout"); r = r ? 1 * r : 20, r = e && e.timeout ? e.timeout : r; const [o, h] = i.split("@"), n = { url: `http://${h}/v1/scripting/evaluate`, body: { script_text: t, mock_type: "cron", timeout: r }, headers: { "X-Key": o, Accept: "*/*" } }; this.post(n, (t, e, i) => s(i)) }).catch(t => this.logErr(t)) } loaddata() { if (!this.isNode()) return {}; { this.fs = this.fs ? this.fs : require("fs"), this.path = this.path ? this.path : require("path"); const t = this.path.resolve(this.dataFile), e = this.path.resolve(process.cwd(), this.dataFile), s = this.fs.existsSync(t), i = !s && this.fs.existsSync(e); if (!s && !i) return {}; { const i = s ? t : e; try { return JSON.parse(this.fs.readFileSync(i)) } catch (t) { return {} } } } } writedata() { if (this.isNode()) { this.fs = this.fs ? this.fs : require("fs"), this.path = this.path ? this.path : require("path"); const t = this.path.resolve(this.dataFile), e = this.path.resolve(process.cwd(), this.dataFile), s = this.fs.existsSync(t), i = !s && this.fs.existsSync(e), r = JSON.stringify(this.data); s ? this.fs.writeFileSync(t, r) : i ? this.fs.writeFileSync(e, r) : this.fs.writeFileSync(t, r) } } lodash_get(t, e, s) { const i = e.replace(/\[(\d+)\]/g, ".$1").split("."); let r = t; for (const t of i) if (r = Object(r)[t], void 0 === r) return s; return r } lodash_set(t, e, s) { return Object(t) !== t ? t : (Array.isArray(e) || (e = e.toString().match(/[^.[\]]+/g) || []), e.slice(0, -1).reduce((t, s, i) => Object(t[s]) === t[s] ? t[s] : t[s] = Math.abs(e[i + 1]) >> 0 == +e[i + 1] ? [] : {}, t)[e[e.length - 1]] = s, t) } getdata(t) { let e = this.getval(t); if (/^@/.test(t)) { const [, s, i] = /^@(.*?)\.(.*?)$/.exec(t), r = s ? this.getval(s) : ""; if (r) try { const t = JSON.parse(r); e = t ? this.lodash_get(t, i, "") : e } catch (t) { e = "" } } return e } setdata(t, e) { let s = !1; if (/^@/.test(e)) { const [, i, r] = /^@(.*?)\.(.*?)$/.exec(e), o = this.getval(i), h = i ? "null" === o ? null : o || "{}" : "{}"; try { const e = JSON.parse(h); this.lodash_set(e, r, t), s = this.setval(JSON.stringify(e), i) } catch (e) { const o = {}; this.lodash_set(o, r, t), s = this.setval(JSON.stringify(o), i) } } else s = this.setval(t, e); return s } getval(t) { return this.isSurge() || this.isLoon() ? $persistentStore.read(t) : this.isQuanX() ? $prefs.valueForKey(t) : this.isNode() ? (this.data = this.loaddata(), this.data[t]) : this.data && this.data[t] || null } setval(t, e) { return this.isSurge() || this.isLoon() ? $persistentStore.write(t, e) : this.isQuanX() ? $prefs.setValueForKey(t, e) : this.isNode() ? (this.data = this.loaddata(), this.data[e] = t, this.writedata(), !0) : this.data && this.data[e] || null } initGotEnv(t) { this.got = this.got ? this.got : require("got"), this.cktough = this.cktough ? this.cktough : require("tough-cookie"), this.ckjar = this.ckjar ? this.ckjar : new this.cktough.CookieJar, t && (t.headers = t.headers ? t.headers : {}, void 0 === t.headers.Cookie && void 0 === t.cookieJar && (t.cookieJar = this.ckjar)) } get(t, e = (() => { })) { t.headers && (delete t.headers["Content-Type"], delete t.headers["Content-Length"]), this.isSurge() || this.isLoon() ? (this.isSurge() && this.isNeedRewrite && (t.headers = t.headers || {}, Object.assign(t.headers, { "X-Surge-Skip-Scripting": !1 })), $httpClient.get(t, (t, s, i) => { !t && s && (s.body = i, s.statusCode = s.status), e(t, s, i) })) : this.isQuanX() ? (this.isNeedRewrite && (t.opts = t.opts || {}, Object.assign(t.opts, { hints: !1 })), $task.fetch(t).then(t => { const { statusCode: s, statusCode: i, headers: r, body: o } = t; e(null, { status: s, statusCode: i, headers: r, body: o }, o) }, t => e(t))) : this.isNode() && (this.initGotEnv(t), this.got(t).on("redirect", (t, e) => { try { if (t.headers["set-cookie"]) { const s = t.headers["set-cookie"].map(this.cktough.Cookie.parse).toString(); s && this.ckjar.setCookieSync(s, null), e.cookieJar = this.ckjar } } catch (t) { this.logErr(t) } }).then(t => { const { statusCode: s, statusCode: i, headers: r, body: o } = t; e(null, { status: s, statusCode: i, headers: r, body: o }, o) }, t => { const { message: s, response: i } = t; e(s, i, i && i.body) })) } post(t, e = (() => { })) { if (t.body && t.headers && !t.headers["Content-Type"] && (t.headers["Content-Type"] = "application/x-www-form-urlencoded"), t.headers && delete t.headers["Content-Length"], this.isSurge() || this.isLoon()) this.isSurge() && this.isNeedRewrite && (t.headers = t.headers || {}, Object.assign(t.headers, { "X-Surge-Skip-Scripting": !1 })), $httpClient.post(t, (t, s, i) => { !t && s && (s.body = i, s.statusCode = s.status), e(t, s, i) }); else if (this.isQuanX()) t.method = "POST", this.isNeedRewrite && (t.opts = t.opts || {}, Object.assign(t.opts, { hints: !1 })), $task.fetch(t).then(t => { const { statusCode: s, statusCode: i, headers: r, body: o } = t; e(null, { status: s, statusCode: i, headers: r, body: o }, o) }, t => e(t)); else if (this.isNode()) { this.initGotEnv(t); const { url: s, ...i } = t; this.got.post(s, i).then(t => { const { statusCode: s, statusCode: i, headers: r, body: o } = t; e(null, { status: s, statusCode: i, headers: r, body: o }, o) }, t => { const { message: s, response: i } = t; e(s, i, i && i.body) }) } } time(t, e = null) { const s = e ? new Date(e) : new Date; let i = { "M+": s.getMonth() + 1, "d+": s.getDate(), "H+": s.getHours(), "m+": s.getMinutes(), "s+": s.getSeconds(), "q+": Math.floor((s.getMonth() + 3) / 3), S: s.getMilliseconds() }; /(y+)/.test(t) && (t = t.replace(RegExp.$1, (s.getFullYear() + "").substr(4 - RegExp.$1.length))); for (let e in i) new RegExp("(" + e + ")").test(t) && (t = t.replace(RegExp.$1, 1 == RegExp.$1.length ? i[e] : ("00" + i[e]).substr(("" + i[e]).length))); return t } msg(e = t, s = "", i = "", r) { const o = t => { if (!t) return t; if ("string" == typeof t) return this.isLoon() ? t : this.isQuanX() ? { "open-url": t } : this.isSurge() ? { url: t } : void 0; if ("object" == typeof t) { if (this.isLoon()) { let e = t.openUrl || t.url || t["open-url"], s = t.mediaUrl || t["media-url"]; return { openUrl: e, mediaUrl: s } } if (this.isQuanX()) { let e = t["open-url"] || t.url || t.openUrl, s = t["media-url"] || t.mediaUrl; return { "open-url": e, "media-url": s } } if (this.isSurge()) { let e = t.url || t.openUrl || t["open-url"]; return { url: e } } } }; if (this.isMute || (this.isSurge() || this.isLoon() ? $notification.post(e, s, i, o(r)) : this.isQuanX() && $notify(e, s, i, o(r))), !this.isMuteLog) { let t = ["", "==============📣系统通知📣=============="]; t.push(e), s && t.push(s), i && t.push(i), console.log(t.join("\n")), this.logs = this.logs.concat(t) } } log(...t) { t.length > 0 && (this.logs = [...this.logs, ...t]), console.log(t.join(this.logSeparator)) } logErr(t, e) { const s = !this.isSurge() && !this.isQuanX() && !this.isLoon(); s ? this.log("", `❗️${this.name}, 错误!`, t.stack) : this.log("", `❗️${this.name}, 错误!`, t) } wait(t) { return new Promise(e => setTimeout(e, t)) } done(t = {}) { const e = (new Date).getTime(), s = (e - this.startTime) / 1e3; this.log("", `🔔${this.name}, 结束! 🕛 ${s} 秒`), this.log(), (this.isSurge() || this.isQuanX() || this.isLoon()) && $done(t) } }(t, e) }