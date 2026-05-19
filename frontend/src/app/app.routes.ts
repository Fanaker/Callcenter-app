import { Routes } from '@angular/router';

import { Home } from './pages/home/home';
import { Planeamiento } from './pages/planeamiento/planeamiento';
import { CrearRq } from './pages/planeamiento/crear-rq';
import { Reclutamiento } from './pages/reclutamiento/reclutamiento';
import { RqDetalle } from './pages/reclutamiento/rq-detalle';
import { ReclutamientoCandidatos } from './pages/reclutamiento/reclutamiento-candidatos/reclutamiento-candidatos';
import { Postular } from './pages/postular/postular';
import { Formacion } from './pages/formacion/formacion';
import { FormacionDetalle } from './pages/formacion/formacion-detalle';

export const routes: Routes = [
  { path: '', component: Home },
  { path: 'planeamiento', component: Planeamiento },
  { path: 'planeamiento/crear-rq', component: CrearRq },
  { path: 'reclutamiento', component: Reclutamiento },
  { path: 'reclutamiento/rq/:codigo/candidatos', component: ReclutamientoCandidatos },
  { path: 'reclutamiento/rq/:codigo', component: RqDetalle },
  { path: 'postular/:codigo', component: Postular },
  { path: 'formacion', component: Formacion },
  { path: 'formacion/rq/:codigo', component: FormacionDetalle }
];