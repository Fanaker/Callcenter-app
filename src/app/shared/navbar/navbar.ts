import { Component } from '@angular/core';
import { Router, RouterLink, RouterLinkActive } from '@angular/router';

@Component({
  selector: 'app-navbar',
  standalone: true,
  imports: [RouterLink, RouterLinkActive],
  templateUrl: './navbar.html',
  styleUrl: './navbar.css'
})
export class Navbar {
  isCollapsed = false;

  constructor(private router: Router) {}

  toggleCollapsed() {
    this.isCollapsed = !this.isCollapsed;
    document.body.classList.toggle('sidebar-collapsed', this.isCollapsed);
  }

  logout() {
    this.router.navigate(['/']);
  }

  reportIssue() {
    alert('Funcionalidad de reportar problema próximamente disponible.');
  }
}