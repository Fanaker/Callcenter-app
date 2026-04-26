import { Component } from '@angular/core';
import { Router, RouterLink } from '@angular/router';

@Component({
  selector: 'app-navbar',
  standalone: true,
  imports: [RouterLink],
  templateUrl: './navbar.html',
  styleUrl: './navbar.css'
})
export class Navbar {
  constructor(private router: Router) {}

  logout() {
    this.router.navigate(['/']);
  }

  reportIssue() {
    alert('Funcionalidad de reportar problema próximamente disponible.');
  }
}