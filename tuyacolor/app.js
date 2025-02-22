const {a, button, p, div, input, span, ul, li, select, option} = van.tags;
const lightModes = [
    "Fade",
    "Flash",
    "Music"
];
const lightPatterns = [
    "Solid",
    "Up",
    "Down",
    "Center",
    "Stripe",
    "Out",
    "In",
    "Rotate",
    "Spiral"
];
const ColorPicker = () => {
    const config = vanX.reactive({
        id: Math.round(Math.random()*30),
        mode: 0,
        pattern: 0,
        speed: 10,
        colors: [{color: "#ffffff"}]
    });
    return div(
        div(
            span(
                "ID: ",
                input({
                    type: "number",
                    min: 0,
                    max: 30,
                    required: true,
                    value: config.id,
                    oninput: e => config.id = parseInt(e.target.value)
                })
            )
        ),
        div(
            span(
                "Mode: ",
                select(
                    {oninput: e => config.mode = parseInt(e.target.value) },
                    ...lightModes.map((v,i) => option({ value: i.toString(), selected: i == config.mode}, v))
                )
            )
        ),
        div(
            span(
                "Pattern: ",
                select(
                    {oninput: e => config.pattern = parseInt(e.target.value) },
                    ...lightPatterns.map((v,i) => option({ value: i.toString(), selected: i == config.pattern}, v))
                )
            )
        ),
        div(
            span(
                "Speed: ",
                () => config.speed,
                input({
                    type: 'range',
                    min: 0,
                    max: 100,
                    required: true,
                    value: config.speed,
                    oninput: e => config.speed = parseInt(e.target.value)
                })
            )
        ),
        div(
            "Colors:",
            vanX.list(ul, config.colors, ({val: v}, deleter) => li(
                span(
                    a({onclick: deleter}, "X"),
                    input({
                        type: "color",
                        value: v.color,
                        oninput: e => v.color = e.target.value
                    }),
                    () => ` ${v.color}`
                )
            )),
            button({onclick: () => config.colors.push({color:"#ffffff"})}, "+")
        ),
        div(
            () => {
                const id = config.id.toString(16).padStart(2,"0");
                const mode = config.mode.toString(16).padStart(2,"0");
                const pattern = config.pattern.toString(16).padStart(2,"0");
                const speed = config.speed.toString(16).padStart(2,"0");
                const colorString = config.colors.map(v => hex2tuya(v.color)).join("")
                const configstring = `${id}${speed}${mode}${pattern}${colorString}`;
                return configstring;
            }
        )
    );
};
van.add(document.body, ColorPicker());