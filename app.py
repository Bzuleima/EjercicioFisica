import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import time
from matplotlib.patches import Rectangle, Circle, FancyArrowPatch, Arc


# =========================
# CONFIG
# =========================

st.set_page_config(page_title="Banda Transportadora")
st.title("Simulación en Tiempo Real")


# =========================
# ESTILO GENERAL
# =========================

st.markdown("""
<style>

h1 {
    font-size: 26px !important;
    margin-bottom: 5px !important;
}

div.stButton > button {
    background-color: #87CEEB;
    color: black;
    font-weight: bold;
    border-radius: 8px;
    height: 45px;
    width: 220px;
    border: none;
}

div.stButton > button:hover {
    background-color: #6CB4D9;
    color: white;
}

</style>
""", unsafe_allow_html=True)


# =========================
# CONTROLES
# =========================

st.sidebar.header("Parámetros")

m = st.sidebar.slider("Masa (kg)", 1.0, 50.0, 15.0)
v_ref = st.sidebar.slider("Velocidad (m/s)", 0.1, 2.0, 0.6)
mu = st.sidebar.slider("Fricción", 0.0, 0.8, 0.25)

kp = st.sidebar.slider("KP", 10, 300, 120)
tau_max = st.sidebar.slider("Torque máx (Nm)", 5, 50, 25)


# =========================
# CONSTANTES
# =========================

g = 9.81
L = 3.0
h = 1.0
d = 2.83
theta = np.deg2rad(18.3)
R = 0.15
eta = 0.9
dt = 0.05


# =========================
# FUERZAS
# =========================

Fg = m * g * np.sin(theta)
Fn = m * g * np.cos(theta)
Ff = mu * Fn


# =========================
# BOTÓN (AHORA ARRIBA)
# =========================

run = st.button("▶ Iniciar simulación")


# =========================
# CONTENEDORES
# =========================

plot_area = st.empty()
info_area = st.empty()


# =========================
# FUNCIÓN ESCENA
# =========================

def crear_figura():

    fig, ax = plt.subplots(figsize=(8, 5))

    ax.set_xlim(-0.8, d + 1)
    ax.set_ylim(-0.8, h + 1)
    ax.set_aspect("equal")

    ax.plot([0, d], [0, 0], "k--")
    ax.plot([d, d], [0, h], "k--")
    ax.plot([0, d], [0, h], lw=6, color="lightgray")

    ax.add_patch(Circle((0, 0), R, color="dimgray"))
    ax.add_patch(Circle((d, h), R, color="dimgray"))

    ax.annotate("d = 2.83 m",
                xy=(0, -0.4), xytext=(d, -0.4),
                arrowprops=dict(arrowstyle="<->"),
                ha="center")

    ax.annotate("h = 1.0 m",
                xy=(-0.4, 0), xytext=(-0.4, h),
                arrowprops=dict(arrowstyle="<->"),
                va="center",
                rotation=90)

    ax.text(d/2 + 0.05, h/2 + 0.15,
            "L = 3.0 m", color="purple", fontsize=10)

    arco = Arc((0, 0), 0.8, 0.8,
               angle=0,
               theta1=0,
               theta2=np.rad2deg(theta),
               color="black",
               lw=1.5)

    ax.add_patch(arco)

    ax.text(0.45, 0.12, "θ = 18.3°", fontsize=10)

    bloque = Rectangle((0, 0), 0.3, 0.25,
                       angle=np.rad2deg(theta),
                       color="deepskyblue")

    ax.add_patch(bloque)

    peso_vec = FancyArrowPatch((0, 0), (0, -0.6),
                               arrowstyle="->",
                               color="red",
                               linewidth=2)

    vel_vec = FancyArrowPatch((0, 0), (0.5, 0.3),
                              arrowstyle="->",
                              color="green",
                              linewidth=2)

    ax.add_patch(peso_vec)
    ax.add_patch(vel_vec)

    ax.set_title("Geometría de la Banda Transportadora")

    return fig, ax, bloque, peso_vec, vel_vec


# =========================
# ESCENA INICIAL
# =========================

fig0, ax0, bloque0, peso0, vel0 = crear_figura()
plot_area.pyplot(fig0)


# =========================
# SIMULACIÓN
# =========================

if run:

    v = 0.0
    s = 0.0

    fig, ax, bloque, peso_vec, vel_vec = crear_figura()

    for step in range(400):

        error = v_ref - v
        tau = kp * error
        tau = np.clip(tau, -tau_max, tau_max)

        Fm = tau * eta / R
        a = (Fm - Fg - Ff) / m

        v += a * dt
        v = max(v, 0)

        s += v * dt

        if s >= L:
            s = L
            v = 0

        x = s * np.cos(theta)
        y = s * np.sin(theta)

        bloque.set_xy((x - 0.15, y - 0.12))

        peso_vec.set_positions((x, y), (x, y - 0.6))

        vel_vec.set_positions(
            (x, y),
            (x + 0.5 * np.cos(theta),
             y + 0.5 * np.sin(theta))
        )

        omega = v / R
        P = tau * omega

        plot_area.pyplot(fig, clear_figure=False)

        info_area.markdown(
            f"""
            **Velocidad:** {v:.2f} m/s  
            **Torque:** {tau:.1f} Nm  
            **Potencia:** {P:.1f} W  
            **Posición:** {s:.2f} m
            """
        )

        time.sleep(dt)