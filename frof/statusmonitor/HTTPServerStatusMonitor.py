from datetime import datetime
import threading

from flask import Flask, jsonify
from flask_cors import CORS


from .StatusMonitor import StatusMonitor


class HTTPServerStatusMonitor(StatusMonitor):
    def __init__(self, fe: "FrofExecutor", port: int = 8111) -> None:
        self.fe = fe
        self.port = port

        self.started_time = datetime.now()
        self.total_job_count = len(self.fe.fp.as_networkx())

        self.app = Flask(__name__)
        CORS(self.app)
        self.app.add_url_rule("/", "home", self._home)
        self.app.add_url_rule("/status", "status", self._status)
        thread = threading.Thread(
            target=self.app.run, kwargs=dict(host="0.0.0.0", port=self.port)
        )
        thread.daemon = True
        thread.start()

    def _home(self):
        return """
        <html>
            <body>
                <div id="app"></div>
                <script src="https://cdn.jsdelivr.net/npm/vue/dist/vue.js"></script>
                <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bulma@0.8.0/css/bulma.min.css">
                <script defer src="https://use.fontawesome.com/releases/v5.3.1/js/all.js"></script>
                <script>
                    function setTitle(title) {
                        if (title) {
                            document.title = title + " | frof monitor";
                        } else {
                            document.title = "frof monitor";
                        }
                    }
                    let Home = Vue.component('Home', {
                        template: `
                        <div>
                            <div class="section">
                                <h1 class="title">frof monitor</h1>
                                <h2 class="subtitle">Started at {{ started_at }}.</h2>
                                <progress class="progress is-large is-success" :value="this.percent_done" max="100">{{this.percent_done}}%</progress>
                            </div>
                            <div class="section">
                                <div class="columns">
                                    <div class="column">
                                        <div class='panel'>
                                            <div class='panel-block' v-for='job in jobs'>
                                            <div class="column is-2">
                                                <span class="icon" v-if="job.status=='running'">
                                                    <i class="fas fa-spinner fa-pulse"></i>
                                                </span>
                                                <span class="tag" :class='classify(job.status)'>
                                                    {{job.type}}
                                                </span>
                                                </div>
                                                <div class="column is-7">
                                                    <code>{{ job.cmd }}</code>
                                                </div>
                                                <div class="column">
                                                    {{ job.env }}
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                        `,
                        props: {
                            'jobs': {type: Array},
                            'started_at': {type: String},
                            'percent_done': {type: Number},
                        },
                        methods: {
                            classify(s) {
                                return {
                                    "running": "is-info",
                                    "pending": ""
                                }[s];
                            }
                        }
                    });

                    var app = new Vue({
                        el: '#app',
                        components: {Home,},
                        template: `
                        <div>
                            <Home
                                :jobs="this.jobs"
                                :started_at="this.started_at"
                                :percent_done="this.pct"
                                />
                        </div>`,
                        created() {
                            console.log("creating...");
                            window.setInterval(() => {
                                fetch("[[URL]]/status").then(res => res.json()).then(res => {
                                    this.jobs = res.remaining_jobs;
                                    this.started_at = res.started_at;
                                    //this.started_at = new Date(res.started_at).toLocaleString();
                                    this.pct = res.pct * 100;
                                    setTitle(`(${Math.ceil(this.pct)}%)`);
                                }).catch(() => {
                                    this.jobs = [];
                                    this.pct = 100;
                                    setTitle(`Idle`);
                                });
                            }, 1000);
                        },
                        data: {
                            jobs: [],
                            started_at: "unknown time",
                            pct: 0
                        }
                    });
                </script>
            </body>
        </html>
        """.replace(
            "[[URL]]", f"http://0.0.0.0:{self.port}"
        )

    def _status(self):
        next_jobs = self.fe.get_next_jobs()
        next_job_count = len(next_jobs)
        remaining_count = len(self.fe.get_current_network())
        return jsonify(
            {
                "started_at": self.started_time,
                "pct": (self.total_job_count - remaining_count) / self.total_job_count,
                "remaining_count": remaining_count,
                "running": next_job_count,
                "remaining_jobs": list(
                    [
                        {
                            "cmd": str(v["job"].cmd),
                            "type": str(type(v["job"]).__name__),
                            "status": "running"
                            if i in [i for i, k in next_jobs]
                            else "pending",
                            "env": v["job"].env,
                        }
                        for i, v in self.fe.get_current_network().nodes(data=True)
                    ]
                ),
            }
        )

    def launch_status(self):
        self.status = ""

    def emit_status(self):
        self.status = ""

